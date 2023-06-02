frappe.ui.form.on("Donation", {
	onload(frm) {
		if (frm.doc.__islocal && !frm.doc.amended_from) {
			get_all_cost_Center(frm);
		}
		if (frm.doc.__islocal) {
			frappe.db.get_single_value("Non Profit Settings", "default_donor").then((value) => {
				frm.set_value('donor', value)
			});
			frm.set_value('journal_entry', null)
			set_last_vocuher_date(frm);
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
		if(!frm.doc.__islocal){
			let payment_id = (frm.doc.payment_id).replace(/^[^,]+/, frm.doc.name);;
			frm.doc.payment_id = payment_id;
			frm.refresh_fields('payment_id')
		}
		hide_naming_fields(frm);
	},
	donor(frm) {
		if(frm.doc.donor){
			set_pan_attachment(frm);
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

function set_last_vocuher_date(frm) {
	frappe.call({
		method: "pedhi_donation.hook.donation.get_last_vocuher_date",
		callback(r) {
			if (r.message) {
				frm.set_value('date', r.message);
			}
			else{
				frm.set_value('date', frappe.datetime.get_today())
			}
		}
	});
}

function hide_naming_fields(frm) {
	frappe.db.get_single_value("Non Profit Settings", "donation_naming_setting").then((value) => {
		if(value == 'Naming Series'){
			frm.set_df_property('user_choice_name',  'hidden', 1);
			frm.set_df_property('naming_series',  'hidden', 0);
		}
		if(value == 'User Choice'){
			frm.set_df_property('user_choice_name',  'hidden', 0);
			frm.set_df_property('naming_series',  'hidden', 1);
		}
	});
}

function set_pan_attachment(frm) {
	frappe.call({
		method: 'pedhi_donation.hook.donation.fetch_pan_attachment',
		args: {
			donor: frm.doc.donor
		},
		callback: function(response) {
			if (response.message) {
				// Set the fetched attachments to the PAN No and Aadhar No field in Donation
				frm.set_value('upload_pan', response.message.upload_pan);
				frm.set_value('upload_aadhar', response.message.upload_aadhar);
			}
		}
	});
}