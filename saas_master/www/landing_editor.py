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
	context.no_breadcrumbs = 1
	context.full_width = 1
	context.body_class = "ml-editor-body"
	context.title = "Landing page editor"
	context.head_html = (
		'<script id="sm-mode-boot">(function(){try{var m=document.cookie.match(/(?:^|; )sm_mode=([^;]*)/);'
		'var v=m?decodeURIComponent(m[1]):"";if(v!=="dark"&&v!=="light"){'
		'v=(window.matchMedia&&window.matchMedia("(prefers-color-scheme: dark)").matches)?"dark":"light";}'
		'document.documentElement.setAttribute("data-sm-mode",v);'
		'document.documentElement.style.colorScheme=v;}catch(e){}})();</script>'
	) + (context.get("head_html") or "")
	return context
