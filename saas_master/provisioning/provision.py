"""Provisioning job: turns a Queued Tenant Site into a live Frappe site.

Enqueued on the long queue from saas_master.api.signup.create_tenant.
Every step is idempotent so Retry (admin action) simply re-enqueues this job.
"""

import json
import os
import shlex
import shutil

import frappe
from frappe.utils import get_bench_path

from saas_master.provisioning.runner import run_command

TENANT_APPS = ["erpnext", "payments", "webshop", "ecommerce_saas", "builder", "seller"]
MIN_FREE_DISK_GB = 2


class StepFailed(Exception):
	def __init__(self, step, detail=""):
		self.step = step
		self.detail = detail
		super().__init__(f"{step}: {detail}")


def _set(tenant, **kwargs):
	for k, v in kwargs.items():
		tenant.db_set(k, v, commit=True)


def verify_root_password(root_pw) -> bool:
	try:
		import pymysql

		db = pymysql.connect(host=frappe.conf.db_host or "localhost", user="root", passwd=root_pw)
		db.close()
		return True
	except Exception:
		return False


def _site_exists(site: str) -> bool:
	return os.path.isdir(os.path.join(get_bench_path(), "sites", site))


def _installed_apps(site: str) -> list[str]:
	"""Installed apps live in the tenant DB (no per-site apps.txt in v15)."""
	import subprocess

	try:
		out = subprocess.check_output(
			["bench", "--site", site, "list-apps"],
			cwd=get_bench_path(),
			text=True,
			timeout=120,
		)
		return [line.split()[0] for line in out.splitlines() if line.strip()]
	except Exception:
		return []


def _bench_execute(site: str, method: str, kwargs: dict, tenant_name: str, step: str) -> tuple[bool, str]:
	command = (
		f"bench --site {site} execute {method} --kwargs {shlex.quote(json.dumps(kwargs))}"
	)
	return run_command(command, tenant_name, step, timeout=600)


def provision_site(tenant_name: str):
	tenant = frappe.get_doc("Tenant Site", tenant_name)
	if tenant.status not in ("Queued", "Provisioning"):
		return

	site = tenant.site_name
	_set(tenant, status="Provisioning", error_message="")

	try:
		root_pw = frappe.conf.saas_mariadb_root_password
		if not root_pw or not verify_root_password(root_pw):
			raise StepFailed("preflight", "MariaDB root password missing or invalid in master site_config")

		free_gb = shutil.disk_usage(get_bench_path()).free / (1024**3)
		if free_gb < MIN_FREE_DISK_GB:
			raise StepFailed("preflight", f"only {free_gb:.1f} GB disk free")

		admin_pw = tenant.get_password("admin_password", raise_exception=False)
		if not admin_pw:
			admin_pw = frappe.generate_hash(length=24)
			tenant.admin_password = admin_pw
			tenant.flags.ignore_permissions = True
			tenant.save()
			frappe.db.commit()
			admin_pw = tenant.get_password("admin_password")

		owner_pw = tenant.get_password("owner_password", raise_exception=False)

		# ---- step 1: create site ----
		_set(tenant, provisioning_step="1/6 create site")
		if not _site_exists(site):
			ok, out = run_command(
				f"bench new-site {site} "
				f"--mariadb-root-password {shlex.quote(root_pw)} "
				f"--admin-password {shlex.quote(admin_pw)} "
				f"--mariadb-user-host-login-scope=%",
				tenant_name,
				"1/6 create site",
				timeout=900,
			)
			if not ok:
				# half-created site is useless; clean it up for a fresh retry
				_drop_site_quiet(site, root_pw, tenant_name)
				raise StepFailed("create site", "bench new-site failed (see Provisioning Log)")

		# ---- step 2: template restore (fast path) or app installs (slow path) ----
		from saas_master.provisioning.templates import pick_template

		template = pick_template(
			tenant.industry,
			preferred_name=getattr(tenant, "preferred_template", None),
		)
		if template:
			_provision_from_template(tenant, template, site, root_pw, admin_pw)
		else:
			for app in TENANT_APPS:
				step = f"2/6 install {app}"
				_set(tenant, provisioning_step=step)
				if app in _installed_apps(site):
					continue
				ok, out = run_command(
					f"bench --site {site} install-app {app}", tenant_name, step, timeout=1500
				)
				if not ok:
					raise StepFailed(f"install {app}", "install-app failed (see Provisioning Log)")

		# ---- step 3: setup wizard ----
		_set(tenant, provisioning_step="3/6 company setup")
		ok, out = _bench_execute(
			site,
			"ecommerce_saas.setup.tenant_setup.complete_setup",
			{
				"company_name": tenant.company_name,
				"country": tenant.country or "Turkey",
				"currency": tenant.currency or "TRY",
				"full_name": tenant.owner_full_name,
				"email": tenant.owner_email,
			},
			tenant_name,
			"3/6 company setup",
		)
		if not ok:
			raise StepFailed("company setup", "setup wizard failed (see Provisioning Log)")

		# ---- step 4: owner user ----
		_set(tenant, provisioning_step="4/6 owner user")
		ok, out = _bench_execute(
			site,
			"ecommerce_saas.setup.tenant_setup.create_owner_user",
			{
				"email": tenant.owner_email,
				"first_name": tenant.owner_full_name,
				"password": owner_pw or "",
			},
			tenant_name,
			"4/6 owner user",
		)
		if not ok:
			raise StepFailed("owner user", "user creation failed (see Provisioning Log)")

		# ---- step 5: store defaults ----
		_set(tenant, provisioning_step="5/6 store defaults")
		ok, out = _bench_execute(
			site,
			"ecommerce_saas.setup.tenant_setup.apply_store_defaults",
			{"company_name": tenant.company_name},
			tenant_name,
			"5/6 store defaults",
		)
		if not ok:
			raise StepFailed("store defaults", "defaults failed (see Provisioning Log)")

		# ---- step 6: TLS + nginx + finalize ----
		_set(tenant, provisioning_step="6/6 ssl + nginx")
		from saas_master.provisioning.ssl import ensure_tenant_ssl

		try:
			ensure_tenant_ssl(site, tenant_name=tenant_name)
		except Exception as ssl_err:
			# Site is usable on HTTP; keep provisioning failed so admin can retry SSL
			raise StepFailed("ssl", str(ssl_err)) from ssl_err

		_set(
			tenant,
			provisioning_step="6/6 done",
			status="Active",
			site_url=f"https://{site}",
			dns_active=1,
		)
		# owner password no longer needed on the master site
		tenant.db_set("owner_password", "", commit=True)

	except StepFailed as e:
		_set(tenant, status="Failed", error_message=str(e))
	except Exception:
		_set(tenant, status="Failed", error_message="unexpected error (see error log)")
		frappe.log_error(title=f"provision_site {site}")


def _provision_from_template(tenant, template, site: str, root_pw: str, admin_pw: str):
	"""Fast path: restore the template backup instead of installing apps."""
	name = tenant.name

	step = f"2/6 restore template {template.name}"
	_set(tenant, provisioning_step=step, used_template=template.name)
	restore_cmd = (
		f"bench --site {site} --force restore {shlex.quote(template.db_backup_path)}"
	)
	if template.public_files_path and os.path.isfile(template.public_files_path):
		restore_cmd += f" --with-public-files {shlex.quote(template.public_files_path)}"
	if template.private_files_path and os.path.isfile(template.private_files_path):
		restore_cmd += f" --with-private-files {shlex.quote(template.private_files_path)}"
	restore_cmd += f" --db-root-password {shlex.quote(root_pw)}"
	ok, out = run_command(restore_cmd, name, step, timeout=1200)
	if not ok:
		raise StepFailed("restore template", "bench restore failed (see Provisioning Log)")

	step = "2/6 migrate restored site"
	_set(tenant, provisioning_step=step)
	ok, out = run_command(f"bench --site {site} migrate", name, step, timeout=1200)
	# CRM on some benches exits non-zero after ImportError but still finishes after_migrate.
	if not ok and "Executing `after_migrate` hooks" in (out or ""):
		ok = True
	if not ok:
		raise StepFailed("migrate", "bench migrate failed (see Provisioning Log)")

	step = "2/6 reset admin password"
	_set(tenant, provisioning_step=step)
	ok, out = run_command(
		f"bench --site {site} set-admin-password {shlex.quote(admin_pw)}", name, step, timeout=120
	)
	if not ok:
		raise StepFailed("admin password", "set-admin-password failed (see Provisioning Log)")

	step = "2/6 scrub source data"
	_set(tenant, provisioning_step=step)
	ok, out = _bench_execute(
		site,
		"ecommerce_saas.setup.tenant_setup.scrub_restored_site",
		{"company_name": tenant.company_name},
		name,
		step,
	)
	if not ok:
		raise StepFailed("scrub", "scrub_restored_site failed (see Provisioning Log)")


def _drop_site_quiet(site: str, root_pw: str, tenant_name: str):
	if _site_exists(site):
		run_command(
			f"bench drop-site {site} --db-root-password {shlex.quote(root_pw)} --force --no-backup",
			tenant_name,
			"cleanup: drop failed site",
			timeout=300,
		)


def enqueue_provisioning(tenant_name: str):
	frappe.enqueue(
		"saas_master.provisioning.provision.provision_site",
		queue="long",
		timeout=3600,
		job_id=f"provision::{tenant_name}",
		deduplicate=True,
		tenant_name=tenant_name,
	)
