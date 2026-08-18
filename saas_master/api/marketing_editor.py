"""Marketing landing page editor — seller-style blocks for flexloopers.com home."""

from __future__ import annotations

import json

import frappe
from frappe.utils import now_datetime

from saas_master.marketing_i18n import DEMO_TEMPLATES, T


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


def _dumps(blocks) -> str:
	return json.dumps(blocks or [], ensure_ascii=False)


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
				{"title_i18n": {}, "desc_i18n": {}, "badge": "available"},
			],
		},
	},
	{
		"type": "audience",
		"group": "content",
		"label": {"en": "Audience", "ar": "الجمهور", "tr": "Kitle"},
		"defaults": {"title_i18n": {}, "items": [{"title_i18n": {}, "desc_i18n": {}}]},
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
		("sol_storefront_t", "sol_storefront_d", "available"),
		("sol_inventory_t", "sol_inventory_d", "available"),
		("sol_orders_t", "sol_orders_d", "available"),
		("sol_lang_t", "sol_lang_d", "available"),
		("sol_pay_t", "sol_pay_d", "coming"),
		("sol_ship_t", "sol_ship_d", "coming"),
	]
	audience_defs = [
		("aud_1_t", "aud_1_d"),
		("aud_2_t", "aud_2_d"),
		("aud_3_t", "aud_3_d"),
		("aud_4_t", "aud_4_d"),
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
					}
					for t, d, badge in pillar_defs
				],
			},
		},
		{
			"id": _uid("audience"),
			"type": "audience",
			"props": {
				"title_i18n": _i18n("sec_audience"),
				"items": [{"title_i18n": _i18n(t), "desc_i18n": _i18n(d)} for t, d in audience_defs],
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


def ensure_marketing_landing(force_seed: bool = False):
	"""Create Single + seed draft/published from current hardcoded landing if empty."""
	if not frappe.db.exists("DocType", "Marketing Landing"):
		return None
	doc = frappe.get_single("Marketing Landing")
	blocks = _parse_blocks(doc.draft_blocks)
	if force_seed or not blocks:
		seed = default_home_blocks()
		doc.draft_blocks = _dumps(seed)
		doc.published_blocks = _dumps(seed)
		doc.status = "Published"
		doc.published_on = now_datetime()
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
	}


@frappe.whitelist()
def save_draft(blocks: str | list | None = None):
	_require_admin()
	doc = ensure_marketing_landing()
	parsed = _parse_blocks(blocks)
	doc.draft_blocks = _dumps(parsed)
	doc.last_saved_on = now_datetime()
	if doc.status != "Published":
		doc.status = "Draft"
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return {"ok": True, "last_saved_on": doc.last_saved_on, "count": len(parsed)}


@frappe.whitelist()
def publish(blocks: str | list | None = None):
	_require_admin()
	doc = ensure_marketing_landing()
	if blocks is not None:
		parsed = _parse_blocks(blocks)
		doc.draft_blocks = _dumps(parsed)
	else:
		parsed = _parse_blocks(doc.draft_blocks)
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
			return blocks or None
	if doc.status != "Published":
		return None
	blocks = _parse_blocks(doc.published_blocks)
	return blocks or None
