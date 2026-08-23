import frappe

from saas_master.api.signup import geo_options
from saas_master.marketing_i18n import LANGS, T, apply_marketing_context, t
from saas_master.saas_master.doctype.signup_aside_step.signup_aside_step import get_signup_aside_steps


def get_context(context):
	apply_marketing_context(context, page="signup")
	geo = geo_options()
	context.geo = geo
	context.geo_json = frappe.as_json(geo)
	# Current lang flat dict (legacy)
	context.signup_i18n_json = frappe.as_json(dict(context.sm))
	# All languages for client-side AR / EN / TR switching without full reload
	context.signup_i18n_all_json = frappe.as_json(
		{lang: {key: t(key, lang) for key in T} for lang in LANGS}
	)
	aside_steps = get_signup_aside_steps()
	context.signup_aside_steps = aside_steps
	context.signup_aside_steps_json = frappe.as_json(aside_steps)
	# First enabled step (or empty) for initial SSR paint
	first = next((s for s in aside_steps if s.get("step") == 1), aside_steps[0] if aside_steps else None)
	lang = context.sm_lang or "en"
	context.signup_aside = _localize_aside(first, lang) if first else None
	return context


def _localize_aside(step: dict, lang: str) -> dict:
	lang = lang if lang in ("en", "ar", "tr") else "en"

	def pick(obj):
		if not isinstance(obj, dict):
			return obj or ""
		return obj.get(lang) or obj.get("en") or ""

	bullets = []
	for b in step.get("bullets") or []:
		text = pick(b.get("text") or {})
		if not text and not b.get("icon"):
			continue
		bullets.append({"icon": b.get("icon") or "", "text": text})
	return {
		"step": step.get("step"),
		"image": step.get("image") or "",
		"kicker": pick(step.get("kicker") or {}),
		"title": pick(step.get("title") or {}),
		"subtitle": pick(step.get("subtitle") or {}),
		"bullets": bullets,
	}
