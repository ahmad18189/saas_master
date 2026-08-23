import frappe

from saas_master.marketing_i18n import LANGS, T, apply_marketing_context, t

# Keys used on the status page (i18n + live language switch)
_STATUS_KEYS = [k for k in T if k.startswith("st_") or k.startswith("feat_")]


def get_context(context):
	apply_marketing_context(context, page="signup-status")
	context.title = t("st_title", context.sm_lang)
	context.status_i18n_json = frappe.as_json({k: t(k, context.sm_lang) for k in _STATUS_KEYS})
	context.status_i18n_all_json = frappe.as_json(
		{lang: {k: t(k, lang) for k in _STATUS_KEYS} for lang in LANGS}
	)
	return context
