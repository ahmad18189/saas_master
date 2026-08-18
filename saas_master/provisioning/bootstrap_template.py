"""One-shot helper to create the default Base Store template (used via bench execute)."""

import frappe


def create_base_template(source_site="demotenant1.milestoneksa.com"):
	if frappe.db.exists("Site Template", "Base Store"):
		print("exists:", frappe.db.get_value("Site Template", "Base Store", "status"))
		return
	doc = frappe.get_doc(
		{
			"doctype": "Site Template",
			"template_name": "Base Store",
			"source_site": source_site,
			"description": "Clean base store: erpnext + payments + webshop + ecommerce_saas, setup complete, no demo data.",
			"is_default": 1,
		}
	)
	doc.insert(ignore_permissions=True)
	frappe.db.commit()
	print("created:", doc.name)
