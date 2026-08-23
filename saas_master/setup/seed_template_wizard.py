"""Seed Site Template wizard preview copy + images (idempotent)."""

from __future__ import annotations

import frappe

from saas_master.api.signup import _INDUSTRY_DEMO_KEY, _demo_by_key


def seed_site_template_wizard_copy(force: bool = False) -> int:
	"""Fill EN/AR/TR titles, descriptions, and image URLs on selectable templates."""
	demos = _demo_by_key()
	updated = 0
	for name in frappe.get_all(
		"Site Template",
		filters={"is_selectable": 1},
		pluck="name",
	):
		doc = frappe.get_doc("Site Template", name)
		demo = demos.get(_INDUSTRY_DEMO_KEY.get(doc.industry or "") or "")
		if not demo:
			continue
		changed = False

		def set_if(field, value):
			nonlocal changed
			if not value:
				return
			if force or not (doc.get(field) or "").strip():
				if doc.get(field) != value:
					doc.set(field, value)
					changed = True

		img = demo.get("image") or ""
		set_if("preview_image_en", img)
		set_if("preview_image_ar", img)
		set_if("preview_image_tr", img)
		if (force or not doc.preview_image) and img:
			doc.preview_image = img
			changed = True

		set_if("wizard_title_en", demo.get("name_en"))
		set_if("wizard_title_ar", demo.get("name_ar") or demo.get("name_en"))
		set_if("wizard_title_tr", demo.get("name_tr") or demo.get("name_en"))
		set_if("wizard_description_en", demo.get("desc_en"))
		set_if("wizard_description_ar", demo.get("desc_ar") or demo.get("desc_en"))
		set_if("wizard_description_tr", demo.get("desc_tr") or demo.get("desc_en"))

		if (force or not doc.preview_primary_color) and demo.get("color"):
			doc.preview_primary_color = demo["color"]
			changed = True
		if (force or not doc.preview_accent_color) and demo.get("accent"):
			doc.preview_accent_color = demo["accent"]
			changed = True

		if changed:
			doc.save(ignore_permissions=True)
			updated += 1

	if updated:
		frappe.db.commit()
	return updated
