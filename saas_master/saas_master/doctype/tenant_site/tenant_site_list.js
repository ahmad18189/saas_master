frappe.listview_settings["Tenant Site"] = {
	add_fields: ["status"],
	get_indicator(doc) {
		const colors = {
			Draft: "gray",
			Queued: "orange",
			Provisioning: "blue",
			Active: "green",
			Failed: "red",
			Suspended: "yellow",
			Dropped: "gray",
		};
		return [__(doc.status), colors[doc.status] || "gray", "status,=," + doc.status];
	},
};
