import frappe


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/landing-editor"
		raise frappe.Redirect

	roles = set(frappe.get_roles())
	if "System Manager" not in roles and frappe.session.user != "Administrator":
		frappe.throw(frappe._("Not permitted"), frappe.PermissionError)

	context.no_cache = 1
	context.no_sidebar = 1
	context.no_header = 1
	context.no_footer = 1
	context.title = "Landing page editor"
	return context
