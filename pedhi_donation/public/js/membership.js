frappe.ui.form.on("Membership", {
	refresh(frm) {
		frm.fields_dict['split_cost_center_table'].grid.get_field('cost_center').get_query = function(doc, cdt, cdn) {
			return {
				filters: [
					['company', '=', doc.company],
					['is_group', '=', 0]
				]
			}
		}
		setTimeout(() => {
			frm.remove_custom_button('Generate Invoice');
		}, 200);

		if(!frm.doc.__islocal && !frm.doc.journal_entry){
			frm.add_custom_button(__("Create Journal Entry"), function() {
				create_journal_entry(frm);
			});
		}

		if(!frm.doc.__islocal && frm.doc.journal_entry){
			frm.add_custom_button(__("Cancel Journal Entry"), function() {
				cancel_journal_entry(frm);
			});
		}
	},
	onload(frm) {
		if (frm.doc.__islocal) {
			frm.set_value('from_date', frappe.datetime.get_today())
		}
	},
	membership_type(frm) {
		get_membership_cost_Center(frm);
	},
	company(frm) {
		if(frm.doc.membership_type){
			get_membership_cost_Center(frm);
		}
	},
	reset_data(frm) {
		if (frm.doc.docstatus == 0) {
			get_membership_cost_Center(frm);
		}
	},
});

function get_membership_cost_Center(frm) {
	frappe.call({
		method: "pedhi_donation.hook.membership.get_membership_cost_Center",
		args: {
			"company": frm.doc.company,
			"membership_type": frm.doc.membership_type
		},
		callback(r) {
			frm.clear_table('split_cost_center_table');
			if (r.message) {
				r.message.forEach((item, i) => {
					let cost_center_table = frm.add_child('split_cost_center_table');
					frappe.model.set_value(cost_center_table.doctype, cost_center_table.name, 'cost_center', item.cost_center);
					frappe.model.set_value(cost_center_table.doctype, cost_center_table.name, 'remarks', item.remarks);
					frappe.model.set_value(cost_center_table.doctype, cost_center_table.name, 'amount', item.amount);
					frappe.model.set_value(cost_center_table.doctype, cost_center_table.name, 'company', item.company);
				})
				frm.refresh_fields('split_cost_center_table');
			}
		}
	});
}

function create_journal_entry(frm) {
	frappe.call({
		method: "pedhi_donation.hook.membership.create_split_cost_center_jv",
		args: {
			membership_id : frm.doc.name,
		},
		callback(r) {
			frm.reload_doc();
		}
	});
}

function cancel_journal_entry(frm) {
	frappe.call({
		method: "pedhi_donation.hook.membership.cancel_journal_entry",
		args: {
			membership_id : frm.doc.name,
		},
		callback(r) {
			frm.reload_doc();
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