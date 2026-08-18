import os
import re

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_bench_path

TEMPLATE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 _-]{2,60}$")


class SiteTemplate(Document):
	def validate(self):
		if not TEMPLATE_NAME_RE.match(self.template_name or ""):
			frappe.throw(_("Template name: 3-61 chars, letters/digits/spaces/dashes/underscores only."))
		source = (self.source_site or "").strip()
		self.source_site = source
		if not os.path.isfile(os.path.join(get_bench_path(), "sites", source, "site_config.json")):
			frappe.throw(_("Source site {0} does not exist on this bench.").format(source))
		if self.is_default:
			# only one default template
			others = frappe.get_all(
				"Site Template", filters={"is_default": 1, "name": ["!=", self.name]}, pluck="name"
			)
			for other in others:
				frappe.db.set_value("Site Template", other, "is_default", 0)

	def slug(self) -> str:
		return frappe.scrub(self.template_name)

	def template_dir(self) -> str:
		return os.path.join(get_bench_path(), "sites", "saas-templates", self.slug())

	def on_trash(self):
		# remove stored backup files with the doc
		import shutil

		if os.path.isdir(self.template_dir()):
			shutil.rmtree(self.template_dir(), ignore_errors=True)
