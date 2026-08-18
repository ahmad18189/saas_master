import frappe

from saas_master.api.marketing_editor import get_published_home_blocks
from saas_master.marketing_i18n import apply_marketing_context


def get_context(context):
	apply_marketing_context(context, page="home")
	preview = bool(frappe.form_dict.get("landing_preview"))
	blocks = get_published_home_blocks(preview=preview)
	context.use_marketing_blocks = bool(blocks)
	context.marketing_blocks = blocks or []

	imgs = []
	for b in blocks or []:
		if b.get("type") == "demos":
			for it in (b.get("props") or {}).get("items") or []:
				if it.get("image"):
					imgs.append(it["image"])
	if not imgs:
		for d in context.get("sm_demos") or []:
			image = d.get("image") if isinstance(d, dict) else getattr(d, "image", None)
			if image:
				imgs.append(image)
	context.marketing_demo_images = imgs
	return context
