import frappe

def execute():
	all_member = frappe.db.get_all('Member', ['name', 'status'])
	for member in all_member:
		if frappe.db.exists('Member', member.name) and frappe.db.exists('Membership', {"member": member.name}):
			membership_doc = frappe.get_last_doc('Membership', {"member": member.name})
			if membership_doc:
				frappe.db.set_value('Member', member.name, {
					'status' : membership_doc.membership_status,
					'lr_no' : membership_doc.name,
					'lr_date' : membership_doc.date
				})