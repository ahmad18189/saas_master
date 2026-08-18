frappe.ui.form.on("Site Template", {
	refresh(frm) {
		if (frm.is_new()) return;

		if (frm.doc.status !== "Building") {
			const label = frm.doc.status === "Ready" ? __("Rebuild Template") : __("Build Template");
			frm.add_custom_button(label, () => {
				frappe.confirm(
					__("Take a fresh backup of {0} and use it as this template?", [frm.doc.source_site]),
					() => {
						frappe.call({
							method: "saas_master.api.admin.build_template",
							args: { template: frm.doc.name },
							freeze: true,
							callback: () => {
								frappe.show_alert({ message: __("Template build queued"), indicator: "blue" });
								frm.reload_doc();
							},
						});
					}
				);
			}).addClass("btn-primary");
		}

		frm.add_custom_button(__("Provisioning Logs"), () => {
			frappe.set_route("List", "Provisioning Log", { step: ["like", "%template%"] });
		});
	},
});
