frappe.listview_settings["Site Template"] = {
	add_fields: ["status", "is_default"],
	get_indicator(doc) {
		const colors = {
			Draft: "gray",
			Building: "blue",
			Ready: "green",
			Failed: "red",
		};
		return [__(doc.status), colors[doc.status] || "gray", "status,=," + doc.status];
	},
};
