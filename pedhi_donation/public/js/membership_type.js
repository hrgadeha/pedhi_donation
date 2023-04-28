frappe.ui.form.on('Membership Type', {
	refresh: function(frm) {
		frm.set_query("cost_center", "split_cost_center_table", function(doc, cdt, cdn) {
			let d = locals[cdt][cdn];
			return {
				filters: [
					['Cost Center', 'is_group', '=', 0],
				]
			};
		});
	},
});

frappe.ui.form.on("Split Cost Center Table", {
	amount: function (frm, cdt, cdn) {
		calculate_amount(frm);
	},
	split_cost_center_table_remove: function (frm, cdt, cdn) {
		calculate_amount(frm);
	}
});

function calculate_amount(frm) {
	let amount = 0;
	let cost_centers = frm.doc.split_cost_center_table;
	for (let j = 0; j < cost_centers.length; j++) {
		amount += cost_centers[j].amount;
	}
	frm.set_value("amount", amount);
}