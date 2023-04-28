frappe.ui.form.on("Donation", {
	onload(frm) {
		if (frm.doc.__islocal) {
			get_all_cost_Center(frm);
			frm.set_value('date', frappe.datetime.get_today())
		}
	},
	refresh(frm) {
		setTimeout(() => {
			frm.remove_custom_button('Create Payment Entry');
		}, 200);
		if(frm.doc.docstatus == 1){
			frm.add_custom_button(__("Open Ledger"), function() {
				frappe.route_options = {
					voucher_no: frm.doc.journal_entry,
					from_date: frm.doc.date,
					to_date: moment(frm.doc.modified).format('YYYY-MM-DD'),
					company: frm.doc.company,
					group_by: "Group by Voucher (Consolidated)",
				};
				frappe.set_route("query-report", "General Ledger");
			});
		}
	},
	company(frm) {
		get_all_cost_Center(frm);
	},
	fetch_cost_centers(frm) {
		if (frm.doc.docstatus == 0) {
			get_all_cost_Center(frm);
		}
	},
});

function get_all_cost_Center(frm) {
	frappe.call({
		method: "pedhi_donation.hook.donation.get_cost_center",
		args: {
			"company": frm.doc.company,
		},
		callback(r) {
			if (r.message) {
				frm.clear_table('split_cost_center_table');
				r.message.forEach((item, i) => {
					let cost_center_table = frm.add_child('split_cost_center_table');
					cost_center_table.cost_center = item.name;
				})
				frm.refresh_fields('split_cost_center_table');
			}
		}
	});
}

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