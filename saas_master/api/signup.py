import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import validate_email_address
import re

from saas_master.marketing_i18n import DEMO_TEMPLATES
from saas_master.saas_master.doctype.tenant_site.tenant_site import subdomain_issue, validate_subdomain

VALID_INDUSTRIES = (
	"Clothing",
	"Electronics",
	"Beauty",
	"Home",
	"Grocery",
	"Services",
	"Other",
)

PREFERRED_COUNTRIES = (
	"Turkey",
	"Saudi Arabia",
	"United Arab Emirates",
	"Egypt",
	"United States",
	"United Kingdom",
	"Germany",
)

PREFERRED_CURRENCIES = ("TRY", "SAR", "AED", "EGP", "USD", "EUR", "GBP")
_ISD_RE = re.compile(r"^\+\d{1,4}$")

# Site Template.industry -> demo niche key
_INDUSTRY_DEMO_KEY = {
	"Clothing": "fashion",
	"Electronics": "electronics",
	"Beauty": "beauty",
	"Home": "home",
}


def _demo_by_key() -> dict:
	return {d["key"]: d for d in DEMO_TEMPLATES}


def preview_defaults_for_industry(industry: str | None) -> dict:
	"""Image + colors for signup cards when Site Template preview fields are empty."""
	demo = _demo_by_key().get(_INDUSTRY_DEMO_KEY.get(industry or "") or "")
	if not demo:
		return {}
	return {
		"preview_image": demo.get("image") or "",
		"preview_primary_color": demo.get("color") or "",
		"preview_accent_color": demo.get("accent") or "",
		"title_i18n": {
			"en": demo.get("name_en") or "",
			"ar": demo.get("name_ar") or demo.get("name_en") or "",
			"tr": demo.get("name_tr") or demo.get("name_en") or "",
		},
		"description_i18n": {
			"en": demo.get("desc_en") or "",
			"ar": demo.get("desc_ar") or demo.get("desc_en") or "",
			"tr": demo.get("desc_tr") or demo.get("desc_en") or "",
		},
		"niche_i18n": {
			"en": demo.get("niche_en") or "",
			"ar": demo.get("niche_ar") or demo.get("niche_en") or "",
			"tr": demo.get("niche_tr") or demo.get("niche_en") or "",
		},
	}


def ensure_template_preview_images(force: bool = False) -> int:
	"""Fill Site Template preview_image (and colors) from niche demos."""
	updated = 0
	for name in frappe.get_all("Site Template", pluck="name"):
		doc = frappe.get_doc("Site Template", name)
		defaults = preview_defaults_for_industry(doc.industry)
		if not defaults:
			continue
		changed = False
		if (force or not doc.preview_image) and defaults.get("preview_image"):
			doc.preview_image = defaults["preview_image"]
			changed = True
		if (force or not doc.preview_primary_color) and defaults.get("preview_primary_color"):
			doc.preview_primary_color = defaults["preview_primary_color"]
			changed = True
		if (force or not doc.preview_accent_color) and defaults.get("preview_accent_color"):
			doc.preview_accent_color = defaults["preview_accent_color"]
			changed = True
		if changed:
			doc.save(ignore_permissions=True)
			updated += 1
	if updated:
		frappe.db.commit()
	return updated


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=30, seconds=60)
def check_subdomain(subdomain: str):
	code = subdomain_issue(subdomain)
	return {
		"available": not code,
		"reason_code": code or "",
		"reason": validate_subdomain(subdomain),
	}


def geo_options() -> dict:
	"""Country names, ITU calling codes (ISD), and currencies from Frappe geo data."""
	from frappe.geo.country_info import get_all

	info = get_all()
	known_countries = set(frappe.get_all("Country", pluck="name", ignore_permissions=True))
	known_currencies = set(frappe.get_all("Currency", pluck="name", ignore_permissions=True))

	countries = []
	for name, data in info.items():
		if name not in known_countries:
			continue
		isd = str(data.get("isd") or "").strip().replace(" ", "")
		if not isd:
			continue
		if not isd.startswith("+"):
			isd = "+" + isd.lstrip("+")
		if not _ISD_RE.match(isd) or isd in ("+0", "+00"):
			continue
		currency = data.get("currency") or ""
		if currency and currency not in known_currencies:
			currency = ""
		countries.append(
			{
				"name": name,
				"code": (data.get("code") or "").upper(),
				"isd": isd,
				"currency": currency,
				"preferred": name in PREFERRED_COUNTRIES,
			}
		)

	pref_rank = {n: i for i, n in enumerate(PREFERRED_COUNTRIES)}
	countries.sort(key=lambda r: (0 if r["preferred"] else 1, pref_rank.get(r["name"], 99), r["name"]))

	seen_isd = set()
	dial_codes = []
	for row in countries:
		if row["isd"] in seen_isd:
			continue
		seen_isd.add(row["isd"])
		dial_codes.append({"isd": row["isd"], "name": row["name"], "code": row["code"]})
	dial_codes.sort(key=lambda d: (len(d["isd"]), d["isd"]))

	currency_names = {c["currency"] for c in countries if c["currency"]}
	currencies = sorted(
		currency_names,
		key=lambda c: (0 if c in PREFERRED_CURRENCIES else 1, PREFERRED_CURRENCIES.index(c) if c in PREFERRED_CURRENCIES else 99, c),
	)

	preferred = [c for c in countries if c["preferred"]]
	rest = [c for c in countries if not c["preferred"]]
	return {
		"countries": countries,
		"preferred": preferred,
		"rest": rest,
		"dial_codes": dial_codes,
		"currencies": currencies,
		"default_country": "Turkey" if "Turkey" in known_countries else (countries[0]["name"] if countries else ""),
	}


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=60, seconds=60)
def list_geo():
	return geo_options()


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=60, seconds=60)
def list_templates():
	"""Public list of Ready selectable templates for the signup wizard."""
	rows = frappe.get_all(
		"Site Template",
		filters={"status": "Ready", "is_selectable": 1},
		fields=[
			"name",
			"template_name",
			"description",
			"industry",
			"preview_image",
			"preview_image_en",
			"preview_image_ar",
			"preview_image_tr",
			"wizard_title_en",
			"wizard_title_ar",
			"wizard_title_tr",
			"wizard_description_en",
			"wizard_description_ar",
			"wizard_description_tr",
			"preview_primary_color",
			"preview_accent_color",
			"sort_order",
			"is_default",
		],
		order_by="sort_order asc, modified desc",
	)
	out = []
	for r in rows:
		defaults = preview_defaults_for_industry(r.industry)
		fallback_title = defaults.get("title_i18n") or {}
		fallback_desc = defaults.get("description_i18n") or {}
		fallback_img = defaults.get("preview_image") or ""

		title_i18n = {
			"en": (r.wizard_title_en or fallback_title.get("en") or r.template_name or r.name or ""),
			"ar": (r.wizard_title_ar or fallback_title.get("ar") or r.wizard_title_en or r.template_name or r.name or ""),
			"tr": (r.wizard_title_tr or fallback_title.get("tr") or r.wizard_title_en or r.template_name or r.name or ""),
		}
		desc_i18n = {
			"en": (r.wizard_description_en or fallback_desc.get("en") or r.description or ""),
			"ar": (r.wizard_description_ar or fallback_desc.get("ar") or r.wizard_description_en or r.description or ""),
			"tr": (r.wizard_description_tr or fallback_desc.get("tr") or r.wizard_description_en or r.description or ""),
		}
		default_img = (r.preview_image or fallback_img or "").strip()
		image_i18n = {
			"en": (r.preview_image_en or default_img or "").strip(),
			"ar": (r.preview_image_ar or default_img or "").strip(),
			"tr": (r.preview_image_tr or default_img or "").strip(),
		}
		out.append(
			{
				"name": r.name,
				"title": title_i18n["en"],
				"title_i18n": title_i18n,
				"description": desc_i18n["en"],
				"description_i18n": desc_i18n,
				"industry": r.industry or "Other",
				"preview_image": image_i18n["en"] or default_img,
				"preview_image_i18n": image_i18n,
				"primary_color": r.preview_primary_color
				or defaults.get("preview_primary_color")
				or "#121212",
				"accent_color": r.preview_accent_color
				or defaults.get("preview_accent_color")
				or "#111111",
				"is_default": int(r.is_default or 0),
			}
		)
	return out


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=3, seconds=3600)
def create_tenant(
	company_name: str,
	industry: str,
	country: str,
	currency: str,
	owner_full_name: str,
	owner_email: str,
	owner_phone: str = "",
	business_domain: str = "",
	subdomain: str = "",
	owner_password: str = "",
	template: str = "",
	website: str = "",  # honeypot — real users never fill this
	company_city: str = "",
	company_description: str = "",
	product_count_band: str = "",
	support_need: str = "",
	signup_plan: str = "",
	referral_source: str = "",
):
	if website:
		frappe.throw(_("Invalid request."))

	company_name = (company_name or "").strip()
	owner_full_name = (owner_full_name or "").strip()
	if not company_name or not owner_full_name:
		frappe.throw(_("Company name and your full name are required."))

	validate_email_address(owner_email, throw=True)

	if not owner_password or len(owner_password) < 8:
		frappe.throw(_("Password must be at least 8 characters."))

	reason = validate_subdomain(subdomain)
	if reason:
		frappe.throw(reason)

	VALID_BANDS = ("under_50", "50_200", "200_1000", "over_1000")
	VALID_SUPPORT = ("community", "chat", "dedicated")
	VALID_PLANS = ("Free", "Growth", "Enterprise")
	VALID_REFERRALS = (
		"google",
		"social",
		"friend",
		"compare_platforms",
		"compare_salla_zid",  # legacy
		"youtube",
		"event",
		"other",
	)

	product_count_band = (product_count_band or "").strip()
	if product_count_band and product_count_band not in VALID_BANDS:
		product_count_band = ""
	support_need = (support_need or "").strip()
	if support_need and support_need not in VALID_SUPPORT:
		support_need = "chat"
	signup_plan = (signup_plan or "").strip()
	if signup_plan not in VALID_PLANS:
		# Suggest from catalog size if missing/invalid
		if product_count_band in ("over_1000",) or support_need == "dedicated":
			signup_plan = "Enterprise"
		elif product_count_band in ("50_200", "200_1000") or support_need == "chat":
			signup_plan = "Growth"
		else:
			signup_plan = "Free"
	referral_source = (referral_source or "").strip()
	if referral_source == "compare_salla_zid":
		referral_source = "compare_platforms"
	if referral_source and referral_source not in VALID_REFERRALS:
		referral_source = "other"

	preferred_template = (template or "").strip() or None
	if preferred_template:
		if not frappe.db.exists("Site Template", preferred_template):
			frappe.throw(_("Selected store template is not available."))
		tmeta = frappe.db.get_value(
			"Site Template",
			preferred_template,
			["status", "is_selectable", "industry"],
			as_dict=True,
		)
		if not tmeta or tmeta.status != "Ready" or not int(tmeta.is_selectable or 0):
			frappe.throw(_("Selected store template is not available."))
		if tmeta.industry and tmeta.industry in VALID_INDUSTRIES:
			industry = tmeta.industry

	if industry not in VALID_INDUSTRIES:
		industry = "Other"
	if not frappe.db.exists("Country", country):
		country = "Turkey"
	if not frappe.db.exists("Currency", currency):
		currency = "TRY"

	ip = frappe.local.request_ip or ""
	# one unfinished signup per IP at a time
	if ip and frappe.db.exists(
		"Tenant Site", {"signup_ip": ip, "status": ["in", ["Queued", "Provisioning"]]}
	):
		frappe.throw(_("You already have a store being created. Please wait for it to finish."))

	tenant = frappe.get_doc(
		{
			"doctype": "Tenant Site",
			"subdomain": subdomain.strip().lower(),
			"status": "Queued",
			"company_name": company_name,
			"company_city": (company_city or "").strip()[:80],
			"company_description": (company_description or "").strip()[:500],
			"industry": industry,
			"country": country,
			"currency": currency,
			"product_count_band": product_count_band,
			"support_need": support_need,
			"signup_plan": signup_plan,
			"referral_source": referral_source,
			"owner_full_name": owner_full_name,
			"owner_email": owner_email.strip().lower(),
			"owner_phone": (owner_phone or "").strip(),
			"business_domain": (business_domain or "").strip(),
			"owner_password": owner_password,
			"preferred_template": preferred_template,
			"signup_ip": ip,
		}
	)
	tenant.insert(ignore_permissions=True)
	frappe.db.commit()

	from saas_master.provisioning.provision import enqueue_provisioning

	enqueue_provisioning(tenant.name)

	return {"token": tenant.status_token, "site_name": tenant.site_name}


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=60, seconds=60)
def get_status(token: str):
	if not token or len(token) < 20:
		frappe.throw(_("Invalid token."))
	name = frappe.db.get_value("Tenant Site", {"status_token": token})
	if not name:
		frappe.throw(_("Not found."), frappe.DoesNotExistError)
	t = frappe.db.get_value(
		"Tenant Site",
		name,
		["status", "provisioning_step", "error_message", "site_name", "site_url", "dns_active"],
		as_dict=True,
	)
	from saas_master.provisioning.urls import tenant_ip_url, tenant_url

	# Prefer HTTPS domain URL; fall back to IP cookie link only if DNS is off.
	canonical = t.site_url or tenant_url(t.site_name)
	open_url = canonical if t.dns_active else tenant_ip_url(t.site_name)
	step = t.provisioning_step or ""
	return {
		"status": t.status,
		"step": step,
		"step_index": _provision_step_index(step, t.status),
		"error": t.error_message if t.status == "Failed" else "",
		"site_name": t.site_name,
		"site_url": open_url,
		"dns_active": t.dns_active,
		"ip_url": tenant_ip_url(t.site_name),
	}


def _provision_step_index(step: str, status: str) -> int:
	"""Map provisioning_step text to checklist index 0–5 (or 6 when done)."""
	if status == "Active":
		return 6
	if not step:
		return 0
	s = step.lower()
	if "1/6" in s or "create site" in s:
		return 0
	if "2/6" in s or "restore" in s or "template" in s or "migrate" in s or "scrub" in s or "install" in s:
		return 1
	if "3/6" in s or "company" in s:
		return 2
	if "4/6" in s or "owner" in s:
		return 3
	if "5/6" in s or "defaults" in s:
		return 4
	if "6/6" in s or "ssl" in s or "https" in s or "nginx" in s:
		return 5
	return 0
