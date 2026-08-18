import frappe

from saas_master.api.signup import geo_options


def get_context(context):
	context.no_cache = 1
	geo = geo_options()
	context.geo = geo
	context.geo_json = frappe.as_json(geo)
	return context
