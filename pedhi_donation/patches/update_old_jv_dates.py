import frappe

def execute():
	all_membership = frappe.db.get_all('Membership', ['name', 'journal_entry', 'date'])
	for membership in all_membership:
		if membership.journal_entry and membership.date:
			frappe.db.set_value('Journal Entry', membership.journal_entry, 'posting_date', membership.date)
			frappe.db.sql("""update `tabGL Entry` set posting_date = '{0}'
				where voucher_no = '{1}';""".format(membership.date,membership.journal_entry))