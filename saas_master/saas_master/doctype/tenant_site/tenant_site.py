import re

import frappe
from frappe import _
from frappe.model.document import Document

SUBDOMAIN_RE = re.compile(r"^[a-z0-9][a-z0-9-]{2,30}$")

RESERVED_SUBDOMAINS = {
	"www", "api", "mail", "smtp", "ftp", "admin", "administrator", "master",
	"saas", "app", "desk", "erp", "erpnext", "frappe", "shop", "store", "blog",
	"docs", "help", "support", "status", "test", "demo", "staging", "dev",
	"cdn", "assets", "static", "portal", "billing", "pay", "payment", "secure",
	"vpn", "ns1", "ns2", "ecomearce",
}

BASE_DOMAIN = "flexloopers.com"


def validate_subdomain(subdomain: str, exclude_tenant: str | None = None) -> str:
	"""Validate a subdomain and return the reason it is unavailable, or '' if OK."""
	subdomain = (subdomain or "").strip().lower()
	if not SUBDOMAIN_RE.match(subdomain):
		return _("Subdomain must be 3-31 characters: lowercase letters, digits and dashes, starting with a letter or digit.")
	if subdomain in RESERVED_SUBDOMAINS:
		return _("This subdomain is reserved.")

	site_name = f"{subdomain}.{BASE_DOMAIN}"
	filters = {"subdomain": subdomain, "status": ["!=", "Dropped"]}
	if exclude_tenant:
		filters["name"] = ["!=", exclude_tenant]
	if frappe.db.exists("Tenant Site", filters):
		return _("This subdomain is already taken.")

	# Also check the bench sites directory (covers manually created sites)
	import os

	from frappe.utils import get_bench_path

	if os.path.isdir(os.path.join(get_bench_path(), "sites", site_name)):
		return _("This subdomain is already taken.")
	return ""


class TenantSite(Document):
	def before_insert(self):
		# runs before autoname (name = site_name)
		self.subdomain = (self.subdomain or "").strip().lower()
		self.site_name = f"{self.subdomain}.{BASE_DOMAIN}"

	def validate(self):
		self.subdomain = (self.subdomain or "").strip().lower()
		if self.is_new():
			reason = validate_subdomain(self.subdomain)
			if reason:
				frappe.throw(reason)
		self.site_name = f"{self.subdomain}.{BASE_DOMAIN}"
		if not self.site_url:
			self.site_url = f"https://{self.site_name}"
		if not self.status_token:
			self.status_token = frappe.generate_hash(length=32)
