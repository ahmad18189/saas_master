"""Re-apply the Ready Base Store template onto an existing tenant (fix catalog/home)."""

import os
import shlex

import frappe
from frappe.utils import get_bench_path

from saas_master.provisioning.runner import run_command


def refresh_tenant_from_template(
	site="browsetest.flexloopers.com",
	template_name="Base Store",
	company_name="Browse Test Store",
	owner_email="browsetest@example.com",
	owner_name="Browse Tester",
	owner_password="BrowseTest#2026x",
):
	template = frappe.get_doc("Site Template", template_name)
	if template.status != "Ready" or not template.db_backup_path:
		raise Exception(f"template {template_name} is not Ready")

	root_pw = frappe.conf.saas_mariadb_root_password
	if not root_pw:
		raise Exception("saas_mariadb_root_password missing in master site_config")
	admin_pw = frappe.generate_hash(length=24)

	restore_cmd = f"bench --site {site} --force restore {shlex.quote(template.db_backup_path)}"
	if template.public_files_path and os.path.isfile(template.public_files_path):
		restore_cmd += f" --with-public-files {shlex.quote(template.public_files_path)}"
	if template.private_files_path and os.path.isfile(template.private_files_path):
		restore_cmd += f" --with-private-files {shlex.quote(template.private_files_path)}"
	restore_cmd += f" --db-root-password {shlex.quote(root_pw)}"

	ok, out = run_command(restore_cmd, site, "refresh: restore template", timeout=1200)
	if not ok:
		raise Exception("restore failed")

	ok, out = run_command(f"bench --site {site} migrate", site, "refresh: migrate", timeout=1200)
	if not ok:
		raise Exception("migrate failed")

	ok, out = run_command(
		f"bench --site {site} set-admin-password {shlex.quote(admin_pw)}",
		site,
		"refresh: admin password",
		timeout=120,
	)
	if not ok:
		raise Exception("admin password failed")

	kwargs = shlex.quote(frappe.as_json({"company_name": company_name}))
	ok, out = run_command(
		f"bench --site {site} execute ecommerce_saas.setup.tenant_setup.scrub_restored_site --kwargs {kwargs}",
		site,
		"refresh: scrub",
		timeout=600,
	)
	if not ok:
		raise Exception("scrub failed")

	ok, out = run_command(
		f"bench --site {site} execute ecommerce_saas.setup.tenant_setup.create_owner_user --kwargs "
		+ shlex.quote(
			frappe.as_json(
				{"email": owner_email, "first_name": owner_name, "password": owner_password}
			)
		),
		site,
		"refresh: owner",
		timeout=300,
	)
	if not ok:
		raise Exception("owner failed")

	ok, out = run_command(
		f"bench --site {site} execute ecommerce_saas.setup.tenant_setup.apply_store_defaults --kwargs {kwargs}",
		site,
		"refresh: defaults",
		timeout=300,
	)
	if not ok:
		raise Exception("defaults failed")

	frappe.db.set_value("Tenant Site", site, "used_template", template_name)
	frappe.db.set_value("Tenant Site", site, "admin_password", admin_pw)
	frappe.db.commit()
	print("refreshed", site, "from", template_name)
