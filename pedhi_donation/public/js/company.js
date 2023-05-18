frappe.ui.form.on("Company", {
	refresh(frm) {
		frm.set_query('donor_account', function(doc) {
			return {
				filters: {
					'company': frm.doc.name,
					'account_Type': 'Receivable'
				}
			}
		})
		frm.set_query('member_account', function(doc) {
			return {
				filters: {
					'company': frm.doc.name,
					'account_Type': 'Receivable'
				}
			}
		})
	}
});
