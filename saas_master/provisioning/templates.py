"""Site Template build job: snapshot a source site's DB + files for fast restores."""

import glob
import os
import shutil

import frappe
from frappe.utils import get_bench_path, now_datetime

from saas_master.provisioning.provision import MIN_FREE_DISK_GB
from saas_master.provisioning.runner import run_command


def build_template(template_name: str):
	template = frappe.get_doc("Site Template", template_name)
	source = template.source_site
	template.db_set("status", "Building", commit=True)

	try:
		free_gb = shutil.disk_usage(get_bench_path()).free / (1024**3)
		if free_gb < MIN_FREE_DISK_GB:
			raise Exception(f"only {free_gb:.1f} GB disk free")

		backups_dir = os.path.join(get_bench_path(), "sites", source, "private", "backups")
		before = set(glob.glob(os.path.join(backups_dir, "*")))

		ok, out = run_command(
			f"bench --site {source} backup --with-files",
			tenant_site=None,
			step=f"template build: backup {source}",
			timeout=1800,
		)
		if not ok:
			raise Exception("bench backup failed (see Provisioning Log)")

		new_files = set(glob.glob(os.path.join(backups_dir, "*"))) - before
		db_file = next((f for f in new_files if "database.sql" in os.path.basename(f)), None)
		# Match on basename only — full path contains ".../private/backups/..."
		pub_file = next(
			(
				f
				for f in new_files
				if os.path.basename(f).endswith("-files.tar")
				and not os.path.basename(f).endswith("-private-files.tar")
			),
			None,
		)
		priv_file = next(
			(f for f in new_files if os.path.basename(f).endswith("-private-files.tar")),
			None,
		)
		if not db_file:
			raise Exception("could not locate the new database backup file")

		dest_dir = template.template_dir()
		os.makedirs(dest_dir, exist_ok=True)
		# stable names; old template files replaced atomically enough for our purposes
		db_dest = os.path.join(dest_dir, "database.sql.gz" if db_file.endswith(".gz") else "database.sql")
		shutil.move(db_file, db_dest)
		pub_dest = priv_dest = ""
		if pub_file:
			pub_dest = os.path.join(dest_dir, "files.tar")
			shutil.move(pub_file, pub_dest)
		if priv_file:
			priv_dest = os.path.join(dest_dir, "private-files.tar")
			shutil.move(priv_file, priv_dest)

		# apps snapshot
		import subprocess

		apps = ""
		try:
			apps = subprocess.check_output(
				["bench", "--site", source, "list-apps"], cwd=get_bench_path(), text=True, timeout=120
			).strip()
		except Exception:
			pass

		template.db_set("db_backup_path", db_dest)
		template.db_set("public_files_path", pub_dest)
		template.db_set("private_files_path", priv_dest)
		template.db_set("apps_snapshot", apps)
		template.db_set("built_on", now_datetime())
		template.db_set("status", "Ready")
		frappe.db.commit()

	except Exception as e:
		template.db_set("status", "Failed", commit=True)
		frappe.log_error(title=f"build_template {template_name}", message=str(e))


def enqueue_template_build(template_name: str):
	frappe.enqueue(
		"saas_master.provisioning.templates.build_template",
		queue="long",
		timeout=2400,
		job_id=f"template-build::{template_name}",
		deduplicate=True,
		template_name=template_name,
	)


def pick_template(industry: str | None = None, preferred_name: str | None = None):
	"""Prefer explicit Ready template, else industry match, else Ready default."""
	if preferred_name and frappe.db.exists("Site Template", preferred_name):
		doc = frappe.get_doc("Site Template", preferred_name)
		if doc.status == "Ready":
			return doc
	if industry:
		match = frappe.get_all(
			"Site Template",
			filters={"status": "Ready", "industry": industry},
			order_by="sort_order asc, modified desc",
			limit=1,
			pluck="name",
		)
		if match:
			return frappe.get_doc("Site Template", match[0])
	default = frappe.get_all(
		"Site Template",
		filters={"status": "Ready", "is_default": 1},
		limit=1,
		pluck="name",
	)
	if default:
		return frappe.get_doc("Site Template", default[0])
	return None
