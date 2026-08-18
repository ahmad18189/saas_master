"""Admin actions on Tenant Site — System Manager only, called from Desk buttons."""

import os
import shlex

import frappe
from frappe import _
from frappe.utils import get_bench_path

from saas_master.provisioning.runner import run_command


def _require_admin():
	if "System Manager" not in frappe.get_roles():
		frappe.throw(_("Not permitted"), frappe.PermissionError)


def _root_pw():
	pw = frappe.conf.saas_mariadb_root_password
	if not pw:
		frappe.throw(_("saas_mariadb_root_password missing from master site_config.json"))
	return pw


@frappe.whitelist()
def retry_provisioning(tenant: str):
	_require_admin()
	doc = frappe.get_doc("Tenant Site", tenant)
	if doc.status not in ("Failed", "Queued"):
		frappe.throw(_("Retry is only allowed for Failed tenants."))
	doc.db_set("status", "Queued")
	doc.db_set("error_message", "")
	frappe.db.commit()

	from saas_master.provisioning.provision import enqueue_provisioning

	enqueue_provisioning(doc.name)
	return "queued"


@frappe.whitelist()
def set_suspended(tenant: str, suspend: int = 1):
	_require_admin()
	doc = frappe.get_doc("Tenant Site", tenant)
	if doc.status not in ("Active", "Suspended"):
		frappe.throw(_("Only Active/Suspended tenants can be toggled."))
	suspend = int(suspend)
	value = "1" if suspend else "0"
	ok, out = run_command(
		f"bench --site {doc.site_name} set-config maintenance_mode {value}",
		doc.name,
		"suspend" if suspend else "unsuspend",
		timeout=120,
	)
	if not ok:
		frappe.throw(_("bench set-config failed — see Provisioning Log."))
	run_command(
		f"bench --site {doc.site_name} set-config pause_scheduler {value}",
		doc.name,
		"suspend-scheduler" if suspend else "unsuspend-scheduler",
		timeout=120,
	)
	doc.db_set("status", "Suspended" if suspend else "Active")
	frappe.db.commit()
	return doc.status


@frappe.whitelist()
def drop_site(tenant: str, confirm_subdomain: str):
	_require_admin()
	doc = frappe.get_doc("Tenant Site", tenant)
	if confirm_subdomain != doc.subdomain:
		frappe.throw(_("Confirmation text does not match the subdomain."))
	if doc.site_name == frappe.local.site:
		frappe.throw(_("Refusing to drop the master site."))
	site_dir = os.path.join(get_bench_path(), "sites", doc.site_name)
	if os.path.isdir(site_dir):
		ok, out = run_command(
			f"bench drop-site {doc.site_name} --db-root-password {shlex.quote(_root_pw())} --force --no-backup",
			doc.name,
			"drop site",
			timeout=600,
		)
		if not ok:
			frappe.throw(_("bench drop-site failed — see Provisioning Log."))
	doc.db_set("status", "Dropped")
	frappe.db.commit()
	return "dropped"


@frappe.whitelist()
def build_template(template: str):
	_require_admin()
	doc = frappe.get_doc("Site Template", template)
	if doc.status == "Building":
		frappe.throw(_("Template is already building."))
	from saas_master.provisioning.templates import enqueue_template_build

	enqueue_template_build(doc.name)
	return "queued"


@frappe.whitelist()
def import_existing_sites():
	"""One-time/idempotent: register bench sites that are not in the Tenant Site registry."""
	_require_admin()
	sites_dir = os.path.join(get_bench_path(), "sites")
	imported = []
	for entry in os.listdir(sites_dir):
		path = os.path.join(sites_dir, entry)
		if not os.path.isdir(path) or not os.path.isfile(os.path.join(path, "site_config.json")):
			continue
		if entry == frappe.local.site:
			continue  # the master itself
		subdomain = entry.split(".")[0]
		if frappe.db.exists("Tenant Site", {"site_name": entry}):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Tenant Site",
				"subdomain": subdomain,
				"status": "Active",
				"company_name": subdomain.title(),
				"owner_full_name": "Imported",
				"owner_email": f"admin@{entry}",
				"site_url": f"https://{entry}",
			}
		)
		# bypass new-subdomain availability check (site already exists on disk)
		doc.site_name = entry
		doc.name = entry
		doc.status_token = frappe.generate_hash(length=32)
		doc.db_insert()
		imported.append(entry)
	frappe.db.commit()
	return imported
