"""Seed Desk artifacts that are not file-synced (Custom HTML Block)."""

from __future__ import annotations

import frappe

BLOCK_NAME = "SaaS Ops Hero"

HTML = """
<div class="saas-ops-hero">
  <div class="saas-ops-hero__copy">
    <p class="saas-ops-hero__eyebrow">Flexloopers control plane</p>
    <h3>SaaS lifecycle desk</h3>
    <p>Acquire → provision → activate → bill → support. Track tenants, templates, and marketing from one workspace.</p>
  </div>
  <div class="saas-ops-hero__actions">
    <a class="btn btn-primary btn-sm" href="/app/tenant-site">Tenants</a>
    <a class="btn btn-default btn-sm" href="/app/dashboard-view/SaaS%20Ops">Dashboard</a>
    <a class="btn btn-default btn-sm" href="/landing-editor" target="_blank" rel="noopener">Landing editor</a>
    <a class="btn btn-default btn-sm" href="/signup" target="_blank" rel="noopener">Signup wizard</a>
  </div>
</div>
"""

STYLE = """
.saas-ops-hero {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem 1.5rem;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.15rem;
  border-radius: 12px;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 55%, #0f766e 140%);
  color: #f8fafc;
}
.saas-ops-hero__eyebrow {
  margin: 0 0 0.25rem;
  font-size: 0.75rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  opacity: 0.75;
}
.saas-ops-hero h3 {
  margin: 0 0 0.35rem;
  color: #fff;
  font-size: 1.15rem;
}
.saas-ops-hero p {
  margin: 0;
  max-width: 42rem;
  color: #e2e8f0;
  font-size: 0.9rem;
  line-height: 1.45;
}
.saas-ops-hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.saas-ops-hero__actions .btn-default {
  background: rgba(255,255,255,0.12);
  border-color: transparent;
  color: #fff;
}
.saas-ops-hero__actions .btn-default:hover {
  background: rgba(255,255,255,0.2);
  color: #fff;
}
"""


def ensure_saas_ops_hero():
	roles = [{"role": "System Manager"}]
	if frappe.db.exists("Custom HTML Block", BLOCK_NAME):
		doc = frappe.get_doc("Custom HTML Block", BLOCK_NAME)
		doc.html = HTML
		doc.style = STYLE
		doc.script = ""
		doc.private = 0
		doc.set("roles", [])
		for r in roles:
			doc.append("roles", r)
		doc.save(ignore_permissions=True)
	else:
		doc = frappe.get_doc(
			{
				"doctype": "Custom HTML Block",
				"name": BLOCK_NAME,
				"private": 0,
				"html": HTML,
				"style": STYLE,
				"script": "",
				"roles": roles,
			}
		)
		doc.insert(ignore_permissions=True)
	frappe.db.commit()
	return doc.name


def after_migrate():
	try:
		from saas_master.api.marketing_editor import ensure_marketing_landing

		ensure_marketing_landing(force_seed=False)
	except Exception:
		frappe.log_error(title="Marketing Landing seed")

	try:
		ensure_saas_ops_hero()
	except Exception:
		frappe.log_error(title="SaaS Ops Hero seed")

	try:
		from saas_master.api.signup import ensure_template_preview_images

		ensure_template_preview_images(force=False)
	except Exception:
		frappe.log_error(title="Site Template preview images seed")
