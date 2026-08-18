frappe.ui.form.on("Tenant Site", {
	refresh(frm) {
		if (frm.is_new()) return;

		if (frm.doc.status === "Failed") {
			frm.add_custom_button(__("Retry Provisioning"), () => {
				frappe.call({
					method: "saas_master.api.admin.retry_provisioning",
					args: { tenant: frm.doc.name },
					freeze: true,
					callback: () => {
						frappe.show_alert({ message: __("Provisioning re-queued"), indicator: "blue" });
						frm.reload_doc();
					},
				});
			}).addClass("btn-primary");
		}

		if (frm.doc.status === "Active" || frm.doc.status === "Suspended") {
			const suspend = frm.doc.status === "Active";
			frm.add_custom_button(suspend ? __("Suspend") : __("Unsuspend"), () => {
				frappe.confirm(
					suspend
						? __("Put {0} into maintenance mode?", [frm.doc.site_name])
						: __("Bring {0} back online?", [frm.doc.site_name]),
					() => {
						frappe.call({
							method: "saas_master.api.admin.set_suspended",
							args: { tenant: frm.doc.name, suspend: suspend ? 1 : 0 },
							freeze: true,
							callback: () => frm.reload_doc(),
						});
					}
				);
			});
		}

		if (frm.doc.status !== "Dropped") {
			frm.add_custom_button(__("Drop Site"), () => {
				frappe.prompt(
					{
						fieldname: "confirm_subdomain",
						fieldtype: "Data",
						label: __("Type the subdomain ({0}) to confirm", [frm.doc.subdomain]),
						reqd: 1,
					},
					(values) => {
						frappe.call({
							method: "saas_master.api.admin.drop_site",
							args: { tenant: frm.doc.name, confirm_subdomain: values.confirm_subdomain },
							freeze: true,
							freeze_message: __("Dropping site — this can take a minute…"),
							callback: () => frm.reload_doc(),
						});
					},
					__("Drop {0} permanently?", [frm.doc.site_name]),
					__("Drop Site")
				);
			});
		}

		frm.add_custom_button(__("Provisioning Logs"), () => {
			frappe.set_route("List", "Provisioning Log", { tenant_site: frm.doc.name });
		});
	},
});
