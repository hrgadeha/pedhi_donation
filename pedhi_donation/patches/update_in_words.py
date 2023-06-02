import frappe
from frappe.utils import money_in_words

def execute():
	all_donation = frappe.db.get_list('Donation', fields=['name','amount'])
	all_membership = frappe.db.get_list('Membership', fields=['name','amount'])

	for donation_id in all_donation:
		frappe.db.set_value('Donation', donation_id.name, 'in_words', money_in_words(donation_id.amount))

	for membership_id in all_membership:
		frappe.db.set_value('Membership', membership_id.name, 'in_words', money_in_words(membership_id.amount))