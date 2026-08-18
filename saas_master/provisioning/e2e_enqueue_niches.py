"""Enqueue E2E test tenants for multi-template signup."""

import frappe

from saas_master.provisioning.provision import enqueue_provisioning


def run():
	tests = [
		("etfash", "Fashion Store", "Clothing", "E2E Fashion Co"),
		("ettech", "Electronics Store", "Electronics", "E2E Tech Co"),
		("etbeau", "Beauty Store", "Beauty", "E2E Beauty Co"),
		("ethome", "Home Store", "Home", "E2E Home Co"),
	]
	out = []
	for sub, tmpl, industry, company in tests:
		existing = frappe.db.get_value("Tenant Site", {"subdomain": sub})
		if existing:
			st = frappe.db.get_value("Tenant Site", existing, "status")
			if st == "Active":
				out.append({"subdomain": sub, "status": st, "action": "skip-active"})
				continue
			if st in ("Queued", "Provisioning"):
				out.append({"subdomain": sub, "status": st, "action": "skip-busy"})
				continue
			if st == "Failed":
				frappe.delete_doc("Tenant Site", existing, force=True, ignore_permissions=True)
				frappe.db.commit()

		doc = frappe.get_doc(
			{
				"doctype": "Tenant Site",
				"subdomain": sub,
				"status": "Queued",
				"company_name": company,
				"industry": industry,
				"country": "Turkey",
				"currency": "TRY",
				"owner_full_name": "E2E Owner",
				"owner_email": f"{sub}@example.com",
				"owner_phone": "+90 555 000 0001",
				"owner_password": "E2ETest#2026x",
				"preferred_template": tmpl,
				"signup_ip": "",
			}
		)
		doc.insert(ignore_permissions=True)
		frappe.db.commit()
		enqueue_provisioning(doc.name)
		out.append(
			{
				"subdomain": sub,
				"status": "Queued",
				"template": tmpl,
				"token": doc.status_token,
				"action": "enqueued",
			}
		)
	return out
