"""Guest helpers for the master marketing login page."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import validate_email_address

from saas_master.provisioning.urls import PUBLIC_IP, TENANT_PORT, tenant_url
from saas_master.saas_master.doctype.tenant_site.tenant_site import SUBDOMAIN_RE

BASE_DOMAIN = "flexloopers.com"
_PROVISIONING = ("Queued", "Provisioning")
_UNAVAILABLE = ("Suspended", "Failed", "Dropped", "Draft")


def _login_url(site_name: str, dns_active: int | bool, site_url: str | None = None) -> str:
	if dns_active:
		base = (site_url or "").strip() or tenant_url(site_name)
		return base.rstrip("/") + "/login"
	# IP cookie fallback — land on /login with ?site=
	return f"http://{PUBLIC_IP}:{TENANT_PORT}/login?site={site_name}"


def _payload_for_tenant(row: dict) -> dict:
	status = row.get("status") or ""
	site_name = row.get("site_name") or ""
	subdomain = row.get("subdomain") or ""
	dns_active = row.get("dns_active")
	site_url = row.get("site_url")

	base = {
		"ok": False,
		"status": status,
		"site_name": site_name,
		"subdomain": subdomain,
		"url": "",
	}

	if status == "Active":
		base["ok"] = True
		base["url"] = _login_url(site_name, dns_active, site_url)
		return base

	if status in _PROVISIONING:
		base["reason"] = "provisioning"
		return base

	base["reason"] = "unavailable"
	return base


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=30, seconds=60)
def resolve_store(subdomain: str = "", email: str = ""):
	"""Resolve a merchant store login URL. Never returns passwords or status tokens."""
	subdomain = (subdomain or "").strip().lower()
	email = (email or "").strip().lower()

	if subdomain:
		return _resolve_by_subdomain(subdomain)
	if email:
		return _resolve_by_email(email)
	frappe.throw(_("Enter a store address or email."))


def _resolve_by_subdomain(subdomain: str) -> dict:
	# Allow paste of full host: fashion.flexloopers.com
	if subdomain.endswith("." + BASE_DOMAIN):
		subdomain = subdomain[: -(len(BASE_DOMAIN) + 1)]
	subdomain = subdomain.replace("https://", "").replace("http://", "").split("/")[0]
	if "." in subdomain:
		# unexpected host — reject as not found
		return {"ok": False, "reason": "not_found", "status": "", "site_name": "", "subdomain": "", "url": ""}

	if not SUBDOMAIN_RE.match(subdomain):
		return {"ok": False, "reason": "not_found", "status": "", "site_name": "", "subdomain": subdomain, "url": ""}

	row = frappe.db.get_value(
		"Tenant Site",
		{"subdomain": subdomain},
		["subdomain", "site_name", "status", "dns_active", "site_url"],
		as_dict=True,
	)
	if not row:
		return {"ok": False, "reason": "not_found", "status": "", "site_name": "", "subdomain": subdomain, "url": ""}
	return _payload_for_tenant(row)


def _resolve_by_email(email: str) -> dict:
	try:
		validate_email_address(email, throw=True)
	except Exception:
		return {"ok": False, "reason": "not_found", "status": "", "site_name": "", "subdomain": "", "url": "", "choices": []}

	rows = frappe.get_all(
		"Tenant Site",
		filters={"owner_email": email},
		fields=["subdomain", "site_name", "status", "dns_active", "site_url"],
		order_by="modified desc",
		limit_page_length=20,
	)
	if not rows:
		return {"ok": False, "reason": "not_found", "status": "", "site_name": "", "subdomain": "", "url": "", "choices": []}

	# Prefer Active stores when listing; still surface provisioning ones for that owner
	usable = [r for r in rows if r.status not in _UNAVAILABLE]
	if not usable:
		usable = rows

	if len(usable) == 1:
		return _payload_for_tenant(usable[0])

	choices = []
	for r in usable:
		item = {
			"subdomain": r.subdomain,
			"site_name": r.site_name,
			"status": r.status,
			"url": "",
		}
		if r.status == "Active":
			item["url"] = _login_url(r.site_name, r.dns_active, r.site_url)
		choices.append(item)

	return {
		"ok": False,
		"reason": "multiple",
		"status": "",
		"site_name": "",
		"subdomain": "",
		"url": "",
		"choices": choices,
	}
