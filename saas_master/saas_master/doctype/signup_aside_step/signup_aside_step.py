# Copyright (c) 2026, Flexloopers and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SignupAsideStep(Document):
	def validate(self):
		if self.step is None or int(self.step) < 1 or int(self.step) > 6:
			frappe.throw(frappe._("Wizard Step must be between 1 and 6"))
		self.step = int(self.step)
		key_by_step = {
			1: "company",
			2: "plan",
			3: "look",
			4: "you",
			5: "address",
			6: "review",
		}
		if not self.step_key:
			self.step_key = key_by_step.get(self.step)
		if not (self.image or self.image_url):
			frappe.throw(frappe._("Upload an image or set an External Image URL"))


def get_signup_aside_steps() -> list[dict]:
	"""Public payload for signup wizard aside (all langs + image)."""
	if not frappe.db.exists("DocType", "Signup Aside Step"):
		return []

	rows = frappe.get_all(
		"Signup Aside Step",
		filters={"enabled": 1},
		fields=[
			"name",
			"step",
			"step_key",
			"image",
			"image_url",
			"kicker_en",
			"kicker_ar",
			"kicker_tr",
			"title_en",
			"title_ar",
			"title_tr",
			"subtitle_en",
			"subtitle_ar",
			"subtitle_tr",
			"bullet_1_icon",
			"bullet_1_en",
			"bullet_1_ar",
			"bullet_1_tr",
			"bullet_2_icon",
			"bullet_2_en",
			"bullet_2_ar",
			"bullet_2_tr",
			"bullet_3_icon",
			"bullet_3_en",
			"bullet_3_ar",
			"bullet_3_tr",
		],
		order_by="step asc",
		ignore_permissions=True,
	)

	out = []
	for r in rows:
		image = (r.get("image") or r.get("image_url") or "").strip()
		out.append(
			{
				"step": int(r.step),
				"key": r.step_key or "",
				"image": image,
				"kicker": {"en": r.kicker_en or "", "ar": r.kicker_ar or "", "tr": r.kicker_tr or ""},
				"title": {"en": r.title_en or "", "ar": r.title_ar or "", "tr": r.title_tr or ""},
				"subtitle": {
					"en": r.subtitle_en or "",
					"ar": r.subtitle_ar or "",
					"tr": r.subtitle_tr or "",
				},
				"bullets": [
					{
						"icon": r.bullet_1_icon or "",
						"text": {
							"en": r.bullet_1_en or "",
							"ar": r.bullet_1_ar or "",
							"tr": r.bullet_1_tr or "",
						},
					},
					{
						"icon": r.bullet_2_icon or "",
						"text": {
							"en": r.bullet_2_en or "",
							"ar": r.bullet_2_ar or "",
							"tr": r.bullet_2_tr or "",
						},
					},
					{
						"icon": r.bullet_3_icon or "",
						"text": {
							"en": r.bullet_3_en or "",
							"ar": r.bullet_3_ar or "",
							"tr": r.bullet_3_tr or "",
						},
					},
				],
			}
		)
	return out
