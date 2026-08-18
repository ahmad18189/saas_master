"""Point Base Store template at the Clothing demo and rebuild."""

import frappe


def retarget_and_build(source_site="ecomearce.milestoneksa.com"):
	doc = frappe.get_doc("Site Template", "Base Store")
	doc.source_site = source_site
	doc.industry = "Clothing"
	doc.description = (
		"Clothing demo storefront: products, images, store-home page "
		f"(from {source_site}). Scrub removes users/secrets; catalog stays."
	)
	doc.is_default = 1
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	print("retargeted:", doc.name, "->", source_site)

	from saas_master.provisioning.templates import build_template

	build_template("Base Store")
	print("status:", frappe.db.get_value("Site Template", "Base Store", "status"))
