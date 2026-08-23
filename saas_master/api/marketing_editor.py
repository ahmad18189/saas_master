"""Marketing landing page editor — seller-style blocks for flexloopers.com home."""

from __future__ import annotations

import json

import frappe
from frappe.utils import now_datetime

from saas_master.marketing_i18n import AUDIENCE_IMAGES, DEMO_TEMPLATES, PILLAR_IMAGES, T


def _require_admin():
	if frappe.session.user == "Guest":
		frappe.throw(frappe._("Login required"), frappe.PermissionError)
	roles = set(frappe.get_roles())
	if "System Manager" not in roles and "Administrator" not in roles:
		frappe.throw(frappe._("Not permitted"), frappe.PermissionError)


def _parse_blocks(raw) -> list:
	if not raw:
		return []
	if isinstance(raw, list):
		return raw
	try:
		data = json.loads(raw)
		return data if isinstance(data, list) else []
	except Exception:
		return []


def _dumps(data) -> str:
	return json.dumps(data if data is not None else [], ensure_ascii=False)


def _parse_obj(raw) -> dict:
	if not raw:
		return {}
	if isinstance(raw, dict):
		return raw
	try:
		data = json.loads(raw)
		return data if isinstance(data, dict) else {}
	except Exception:
		return {}


def default_chrome() -> dict:
	return {
		"brand_mark": "Dukan",
		"announcement_i18n": _i18n("announcement"),
		"nav_solutions_i18n": _i18n("nav_solutions"),
		"nav_pricing_i18n": _i18n("nav_pricing"),
		"nav_templates_i18n": _i18n("nav_templates"),
		"nav_login_i18n": _i18n("nav_login"),
		"cta_create_i18n": _i18n("cta_create"),
		"nav_solutions_url": "/solutions",
		"nav_pricing_url": "/pricing",
		"nav_templates_url": "#templates",
		"nav_login_url": "/login",
		"cta_create_url": "/signup",
		"footer_copy_i18n": _i18n("footer_copy"),
		"footer_legal_i18n": _i18n("footer_copy"),
		"copyright_year": now_datetime().strftime("%Y"),
		"footer_contact_i18n": _i18n("footer_contact"),
		"contact_email": "dev@flexloopers.com",
		"contact_url": "https://flexloopers.com",
		"contact_url_label": "flexloopers.com",
		"badge_available_i18n": _i18n("badge_available"),
		"badge_coming_i18n": _i18n("badge_coming"),
	}


def merge_chrome(stored: dict | None) -> dict:
	out = default_chrome()
	if stored:
		out.update(stored)
	return out


def _resolve_map(mapping, lang: str, fallback: str = "") -> str:
	if not isinstance(mapping, dict):
		return fallback
	return mapping.get(lang) or mapping.get("en") or mapping.get("ar") or fallback


def href_with_lang(url: str, lang: str) -> str:
	url = (url or "").strip() or "/"
	if url.startswith(("#", "mailto:", "tel:", "javascript:")):
		return url
	if url.startswith(("http://", "https://")) or "lang=" in url:
		return url
	sep = "&" if "?" in url else "?"
	return f"{url}{sep}lang={lang}"


def brand_mark_html(mark: str) -> str:
	from frappe.utils import escape_html

	mark = (mark or "Dukan").strip() or "Dukan"
	if len(mark) > 2:
		return escape_html(mark[:2]) + "<span>" + escape_html(mark[2:]) + "</span>"
	return escape_html(mark)


def get_effective_chrome(preview: bool = False) -> dict:
	if not frappe.db.exists("DocType", "Marketing Landing"):
		return default_chrome()
	try:
		doc = frappe.get_cached_doc("Marketing Landing")
	except Exception:
		return default_chrome()
	use_draft = False
	if preview and frappe.session.user != "Guest":
		roles = set(frappe.get_roles())
		if "System Manager" in roles or frappe.session.user == "Administrator":
			use_draft = True
	raw = doc.get("draft_chrome") if use_draft else doc.get("published_chrome")
	stored = _parse_obj(raw)
	if not stored and use_draft:
		stored = _parse_obj(doc.get("published_chrome"))
	return merge_chrome(stored)


def overlay_chrome_on_context(context):
	"""Apply saved header/footer copy onto marketing page context (`sm`)."""
	preview = bool(frappe.form_dict.get("landing_preview")) if getattr(frappe, "form_dict", None) else False
	chrome = get_effective_chrome(preview=preview)
	lang = getattr(context, "sm_lang", None) or "en"
	sm = context.get("sm")
	if sm is None:
		return context
	for key in (
		"announcement",
		"nav_solutions",
		"nav_pricing",
		"nav_templates",
		"nav_login",
		"cta_create",
		"footer_copy",
		"footer_contact",
		"badge_available",
		"badge_coming",
	):
		val = _resolve_map(chrome.get(f"{key}_i18n"), lang, sm.get(key) or "")
		if val:
			sm[key] = val
	sm.brand_mark = chrome.get("brand_mark") or "Dukan"
	sm.footer_legal = _resolve_map(
		chrome.get("footer_legal_i18n"), lang, sm.get("footer_copy") or ""
	)
	sm.copyright_year = chrome.get("copyright_year") or now_datetime().strftime("%Y")
	sm.contact_email = chrome.get("contact_email") or "dev@flexloopers.com"
	sm.contact_url = chrome.get("contact_url") or "https://flexloopers.com"
	sm.contact_url_label = chrome.get("contact_url_label") or "flexloopers.com"
	sm.home_href = href_with_lang("/", lang)
	sm.nav_solutions_href = href_with_lang(chrome.get("nav_solutions_url") or "/solutions", lang)
	sm.nav_pricing_href = href_with_lang(chrome.get("nav_pricing_url") or "/pricing", lang)
	sm.nav_templates_href = href_with_lang(chrome.get("nav_templates_url") or "#templates", lang)
	sm.nav_login_href = href_with_lang(chrome.get("nav_login_url") or "/login", lang)
	sm.cta_create_href = href_with_lang(chrome.get("cta_create_url") or "/signup", lang)
	context.sm_brand_html = brand_mark_html(sm.brand_mark)
	return context


def _i18n(key: str) -> dict:
	row = T.get(key) or {}
	return {k: row[k] for k in ("en", "ar", "tr") if row.get(k)}


def _uid(prefix: str) -> str:
	import random
	import string

	return prefix + "_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=7))


BLOCK_CATALOG = [
	{
		"type": "hero",
		"group": "layout",
		"label": {"en": "Hero", "ar": "البانر الرئيسي", "tr": "Hero"},
		"defaults": {
			"brand_mark": "Dukan",
			"title_i18n": {},
			"subtitle_i18n": {},
			"image": "",
			"cta_primary_label_i18n": {},
			"cta_primary_url": "/signup",
			"cta_secondary_label_i18n": {},
			"cta_secondary_url": "#templates",
		},
	},
	{
		"type": "proof",
		"group": "layout",
		"label": {"en": "Proof bar", "ar": "شريط الإثبات", "tr": "Kanıt çubuğu"},
		"defaults": {"line_i18n": {}, "stats": [{"text_i18n": {}}, {"text_i18n": {}}, {"text_i18n": {}}]},
	},
	{
		"type": "pillars",
		"group": "content",
		"label": {"en": "Feature pillars", "ar": "الميزات", "tr": "Özellikler"},
		"defaults": {
			"title_i18n": {},
			"subtitle_i18n": {},
			"link_label_i18n": {},
			"link_url": "/solutions",
			"items": [
				{"title_i18n": {}, "desc_i18n": {}, "badge": "available", "image": ""},
			],
		},
	},
	{
		"type": "audience",
		"group": "content",
		"label": {"en": "Audience", "ar": "الجمهور", "tr": "Kitle"},
		"defaults": {"title_i18n": {}, "items": [{"title_i18n": {}, "desc_i18n": {}, "image": ""}]},
	},
	{
		"type": "demos",
		"group": "content",
		"label": {"en": "Demo stores", "ar": "متاجر تجريبية", "tr": "Demo mağazalar"},
		"defaults": {
			"title_i18n": {},
			"subtitle_i18n": {},
			"open_label_i18n": {},
			"items": [],
		},
	},
	{
		"type": "steps",
		"group": "content",
		"label": {"en": "How it works", "ar": "كيف يعمل", "tr": "Nasıl çalışır"},
		"defaults": {"title_i18n": {}, "items": [{"title_i18n": {}, "desc_i18n": {}}]},
	},
	{
		"type": "diff",
		"group": "content",
		"label": {"en": "Differentiator", "ar": "التميّز", "tr": "Fark"},
		"defaults": {"title_i18n": {}, "subtitle_i18n": {}, "image": ""},
	},
	{
		"type": "cta_banner",
		"group": "interaction",
		"label": {"en": "CTA banner", "ar": "دعوة لاتخاذ إجراء", "tr": "CTA bandı"},
		"defaults": {
			"title_i18n": {},
			"subtitle_i18n": {},
			"cta_label_i18n": {},
			"cta_url": "/signup",
			"use_demo_mosaic": 1,
		},
	},
	{
		"type": "html",
		"group": "advanced",
		"label": {"en": "Custom HTML", "ar": "HTML مخصص", "tr": "Özel HTML"},
		"defaults": {"html": ""},
	},
	{
		"type": "spacer",
		"group": "other",
		"label": {"en": "Spacer", "ar": "مسافة", "tr": "Boşluk"},
		"defaults": {"height": 40},
	},
]


def default_home_blocks() -> list:
	"""Build the current landing structure as editable blocks (AR/EN/TR)."""
	demos = []
	for d in DEMO_TEMPLATES:
		demos.append(
			{
				"key": d["key"],
				"name_i18n": {
					"en": d.get("name_en") or "",
					"ar": d.get("name_ar") or "",
					"tr": d.get("name_tr") or "",
				},
				"niche_i18n": {
					"en": d.get("niche_en") or "",
					"ar": d.get("niche_ar") or "",
					"tr": d.get("niche_tr") or "",
				},
				"color": d.get("color") or "#111",
				"accent": d.get("accent") or "#111",
				"image": d.get("image") or "",
				"url": f"https://{d['key']}.flexloopers.com/",
			}
		)

	pillar_defs = [
		("sol_storefront_t", "sol_storefront_d", "available", PILLAR_IMAGES[0]),
		("sol_inventory_t", "sol_inventory_d", "available", PILLAR_IMAGES[1]),
		("sol_orders_t", "sol_orders_d", "available", PILLAR_IMAGES[2]),
		("sol_lang_t", "sol_lang_d", "available", PILLAR_IMAGES[3]),
		("sol_pay_t", "sol_pay_d", "coming", PILLAR_IMAGES[4]),
		("sol_ship_t", "sol_ship_d", "coming", PILLAR_IMAGES[5]),
	]
	audience_defs = [
		("aud_1_t", "aud_1_d", AUDIENCE_IMAGES[0]),
		("aud_2_t", "aud_2_d", AUDIENCE_IMAGES[1]),
		("aud_3_t", "aud_3_d", AUDIENCE_IMAGES[2]),
		("aud_4_t", "aud_4_d", AUDIENCE_IMAGES[3]),
	]
	step_defs = [
		("how_1_t", "how_1_d"),
		("how_2_t", "how_2_d"),
		("how_3_t", "how_3_d"),
		("how_4_t", "how_4_d"),
	]

	return [
		{
			"id": _uid("hero"),
			"type": "hero",
			"props": {
				"brand_mark": "Dukan",
				"title_i18n": _i18n("hero_title"),
				"subtitle_i18n": _i18n("hero_sub"),
				"image": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=2000&q=80",
				"cta_primary_label_i18n": _i18n("cta_create_free"),
				"cta_primary_url": "/signup",
				"cta_secondary_label_i18n": _i18n("cta_demos"),
				"cta_secondary_url": "#templates",
			},
		},
		{
			"id": _uid("proof"),
			"type": "proof",
			"props": {
				"line_i18n": _i18n("proof_line"),
				"stats": [
					{"text_i18n": _i18n("proof_1")},
					{"text_i18n": _i18n("proof_2")},
					{"text_i18n": _i18n("proof_3")},
				],
			},
		},
		{
			"id": _uid("pillars"),
			"type": "pillars",
			"props": {
				"title_i18n": _i18n("sec_solutions"),
				"subtitle_i18n": _i18n("sec_solutions_sub"),
				"link_label_i18n": _i18n("nav_solutions"),
				"link_url": "/solutions",
				"items": [
					{
						"title_i18n": _i18n(t),
						"desc_i18n": _i18n(d),
						"badge": badge,
						"image": image,
					}
					for t, d, badge, image in pillar_defs
				],
			},
		},
		{
			"id": _uid("audience"),
			"type": "audience",
			"props": {
				"title_i18n": _i18n("sec_audience"),
				"items": [
					{"title_i18n": _i18n(t), "desc_i18n": _i18n(d), "image": image} for t, d, image in audience_defs
				],
			},
		},
		{
			"id": _uid("demos"),
			"type": "demos",
			"props": {
				"title_i18n": _i18n("sec_templates"),
				"subtitle_i18n": _i18n("sec_templates_sub"),
				"open_label_i18n": _i18n("open_demo"),
				"items": demos,
			},
		},
		{
			"id": _uid("steps"),
			"type": "steps",
			"props": {
				"title_i18n": _i18n("sec_how"),
				"items": [{"title_i18n": _i18n(t), "desc_i18n": _i18n(d)} for t, d in step_defs],
			},
		},
		{
			"id": _uid("diff"),
			"type": "diff",
			"props": {
				"title_i18n": _i18n("sec_diff"),
				"subtitle_i18n": _i18n("sec_diff_sub"),
				"image": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=1200&h=900&q=80",
			},
		},
		{
			"id": _uid("cta"),
			"type": "cta_banner",
			"props": {
				"title_i18n": _i18n("banner_title"),
				"subtitle_i18n": _i18n("banner_sub"),
				"cta_label_i18n": _i18n("cta_get_started"),
				"cta_url": "/signup",
				"use_demo_mosaic": 1,
			},
		},
	]


ITEM_IMAGE_POOLS = {
	"pillars": PILLAR_IMAGES,
	"audience": AUDIENCE_IMAGES,
}


DEAD_IMAGE_MARKERS = (
	"1472851298512-d106a2874f3f",
)


def fill_pillar_images(blocks: list) -> tuple[list, bool]:
	"""Attach stock photos to pillar/audience items that have no image yet."""
	changed = False
	for block in blocks or []:
		if not isinstance(block, dict):
			continue
		pool = ITEM_IMAGE_POOLS.get(block.get("type")) or []
		if not pool:
			continue
		props = block.get("props")
		if not isinstance(props, dict):
			continue
		items = props.get("items") or []
		for i, item in enumerate(items):
			if not isinstance(item, dict):
				continue
			current = (item.get("image") or "").strip()
			if current and not any(marker in current for marker in DEAD_IMAGE_MARKERS):
				continue
			item["image"] = pool[i % len(pool)]
			changed = True
	return blocks, changed


def _unsplash_fallback(query: str) -> list:
	q = (query or "").lower()
	picked = list(PILLAR_IMAGES) + list(AUDIENCE_IMAGES)
	if any(w in q for w in ("pay", "card", "checkout", "pos")):
		picked = [PILLAR_IMAGES[4], PILLAR_IMAGES[0]] + picked
	elif any(w in q for w in ("ship", "deliver", "truck", "cargo")):
		picked = [PILLAR_IMAGES[5], PILLAR_IMAGES[2]] + picked
	elif any(w in q for w in ("stock", "invent", "warehouse", "erp")):
		picked = [PILLAR_IMAGES[1], PILLAR_IMAGES[2]] + picked
	elif any(w in q for w in ("order", "return", "package", "box")):
		picked = [PILLAR_IMAGES[2], PILLAR_IMAGES[5]] + picked
	elif any(w in q for w in ("lang", "arabic", "rtl", "translat")):
		picked = [PILLAR_IMAGES[3], PILLAR_IMAGES[0]] + picked
	elif any(w in q for w in ("idea", "start", "launch", "template")):
		picked = [AUDIENCE_IMAGES[0], PILLAR_IMAGES[0]] + picked
	elif any(w in q for w in ("physical", "shelf", "shop", "retail")):
		picked = [AUDIENCE_IMAGES[1], PILLAR_IMAGES[0]] + picked
	elif any(w in q for w in ("online", "already", "invoice")):
		picked = [AUDIENCE_IMAGES[2], PILLAR_IMAGES[4]] + picked
	elif any(w in q for w in ("grow", "brand", "scale", "role")):
		picked = [AUDIENCE_IMAGES[3], PILLAR_IMAGES[1]] + picked
	elif any(w in q for w in ("store", "front", "catalog")):
		picked = [PILLAR_IMAGES[0], PILLAR_IMAGES[1]] + picked
	seen = set()
	out = []
	for url in picked:
		if url in seen:
			continue
		seen.add(url)
		out.append({"url": url, "thumb": url})
	return out


def _search_openverse(query: str) -> list:
	import json
	import urllib.parse
	import urllib.request

	params = urllib.parse.urlencode({"q": query, "page_size": 8, "mature": "false"})
	req = urllib.request.Request(
		"https://api.openverse.org/v1/images/?" + params,
		headers={"User-Agent": "DukanLandingEditor/1.0 (flexloopers.com)", "Accept": "application/json"},
	)
	try:
		with urllib.request.urlopen(req, timeout=8) as resp:
			data = json.loads(resp.read().decode("utf-8"))
	except Exception:
		return []
	out = []
	for row in data.get("results") or []:
		url = (row.get("url") or "").strip()
		if not url:
			continue
		out.append({"url": url, "thumb": (row.get("thumbnail") or url).strip(), "title": row.get("title") or ""})
	return out


@frappe.whitelist()
def fetch_stock_image(query: str | None = None):
	"""Search the public web for a stock photo matching the pillar title."""
	_require_admin()
	q = (query or "").strip() or "online store"
	images = _search_openverse(q)
	if not images:
		images = _unsplash_fallback(q)
	return {"query": q, "images": images[:8]}


def ensure_marketing_landing(force_seed: bool = False):
	"""Create Single + seed draft/published from current hardcoded landing if empty."""
	if not frappe.db.exists("DocType", "Marketing Landing"):
		return None
	doc = frappe.get_single("Marketing Landing")
	blocks = _parse_blocks(doc.draft_blocks)
	chrome = _parse_obj(doc.get("draft_chrome"))
	changed = False
	if force_seed or not blocks:
		seed = default_home_blocks()
		doc.draft_blocks = _dumps(seed)
		doc.published_blocks = _dumps(seed)
		doc.status = "Published"
		doc.published_on = now_datetime()
		doc.last_saved_on = now_datetime()
		changed = True
		blocks = seed
	blocks, img_changed = fill_pillar_images(blocks)
	if img_changed:
		doc.draft_blocks = _dumps(blocks)
		changed = True
	pub = _parse_blocks(doc.published_blocks)
	pub, pub_img = fill_pillar_images(pub)
	if pub_img:
		doc.published_blocks = _dumps(pub)
		changed = True
	if force_seed or not chrome:
		seed_chrome = _dumps(default_chrome())
		doc.draft_chrome = seed_chrome
		if force_seed or not _parse_obj(doc.get("published_chrome")):
			doc.published_chrome = seed_chrome
		doc.last_saved_on = now_datetime()
		changed = True
	if changed:
		doc.last_saved_on = now_datetime()
		doc.save(ignore_permissions=True)
		frappe.db.commit()
	return doc


@frappe.whitelist()
def catalog():
	_require_admin()
	return BLOCK_CATALOG


@frappe.whitelist()
def get_page():
	_require_admin()
	doc = ensure_marketing_landing()
	return {
		"status": doc.status,
		"draft_blocks": _parse_blocks(doc.draft_blocks),
		"published_blocks": _parse_blocks(doc.published_blocks),
		"published_on": doc.published_on,
		"last_saved_on": doc.last_saved_on,
		"catalog": BLOCK_CATALOG,
		"chrome": merge_chrome(_parse_obj(doc.get("draft_chrome"))),
	}


@frappe.whitelist()
def save_draft(blocks: str | list | None = None, chrome=None):
	_require_admin()
	doc = ensure_marketing_landing()
	parsed = _parse_blocks(blocks)
	doc.draft_blocks = _dumps(parsed)
	if chrome is not None:
		doc.draft_chrome = _dumps(merge_chrome(_parse_obj(chrome)))
	doc.last_saved_on = now_datetime()
	if doc.status != "Published":
		doc.status = "Draft"
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return {"ok": True, "last_saved_on": doc.last_saved_on, "count": len(parsed)}


@frappe.whitelist()
def publish(blocks: str | list | None = None, chrome=None):
	_require_admin()
	doc = ensure_marketing_landing()
	if blocks is not None:
		parsed = _parse_blocks(blocks)
		doc.draft_blocks = _dumps(parsed)
	else:
		parsed = _parse_blocks(doc.draft_blocks)
	if chrome is not None:
		merged = merge_chrome(_parse_obj(chrome))
		doc.draft_chrome = _dumps(merged)
		doc.published_chrome = _dumps(merged)
	else:
		doc.published_chrome = doc.draft_chrome or _dumps(default_chrome())
	doc.published_blocks = _dumps(parsed)
	doc.status = "Published"
	doc.published_on = now_datetime()
	doc.last_saved_on = now_datetime()
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	frappe.clear_cache()
	return {"ok": True, "published_on": doc.published_on, "count": len(parsed)}


@frappe.whitelist()
def reset_to_default():
	_require_admin()
	doc = ensure_marketing_landing(force_seed=True)
	return {
		"ok": True,
		"draft_blocks": _parse_blocks(doc.draft_blocks),
		"chrome": merge_chrome(_parse_obj(doc.get("draft_chrome"))),
		"status": doc.status,
	}


def get_published_home_blocks(preview: bool = False) -> list | None:
	"""Return published (or draft if preview+admin) blocks, or None to use static Jinja."""
	if not frappe.db.exists("DocType", "Marketing Landing"):
		return None
	try:
		doc = frappe.get_cached_doc("Marketing Landing")
	except Exception:
		return None
	if preview and frappe.session.user != "Guest":
		roles = set(frappe.get_roles())
		if "System Manager" in roles or frappe.session.user == "Administrator":
			blocks = _parse_blocks(doc.draft_blocks)
			blocks, _ = fill_pillar_images(blocks)
			return blocks or None
	if doc.status != "Published":
		return None
	blocks = _parse_blocks(doc.published_blocks)
	blocks, _ = fill_pillar_images(blocks)
	return blocks or None
