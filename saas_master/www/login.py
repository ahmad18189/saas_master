"""Master marketing login — merchant store finder + operator Frappe auth."""

from frappe.www.login import get_context as frappe_login_context

import frappe

from saas_master.marketing_i18n import LANGS, T, apply_marketing_context, t


def get_context(context):
	frappe_login_context(context)
	apply_marketing_context(context, page="login")

	context.no_cache = 1
	context.no_header = True
	context.show_sidebar = False
	context.show_footer_on_login = 0
	context.full_width = True
	# Force disable Frappe website signup — merchants use /signup
	context.disable_signup = 1
	context.hide_login = True

	context.login_i18n_json = frappe.as_json(dict(context.sm))
	context.login_i18n_all_json = frappe.as_json(
		{lang: {key: t(key, lang) for key in T} for lang in LANGS}
	)
	return context
