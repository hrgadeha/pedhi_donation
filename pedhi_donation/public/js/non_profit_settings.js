frappe.ui.form.on("Non Profit Settings", {
	refresh(frm) {
		frm.set_query('donor_account', function(doc) {
			return {
				filters: {
					'company': frm.doc.company,
					'account_Type': 'Receivable'
				}
			}
		})
		frm.set_query('member_account', function(doc) {
			return {
				filters: {
					'company': frm.doc.company,
					'account_Type': 'Receivable'
				}
			}
		})
	}
});
