import frappe
from frappe import _

def on_cancel(doc, method):
	cancel_donation(doc)

def cancel_donation(doc):
	doc.ignore_linked_doctypes = ("GL Entry", "Payment Ledger Entry", "Donation")
	if doc.donation and frappe.db.exists('Donation', doc.donation):
		donation_doc = frappe.get_doc('Donation', doc.donation)
		if donation_doc.docstatus == 1:
			donation_doc.flags.ignore_permissions = True
			donation_doc.ignore_linked_doctypes = ("GL Entry", "Payment Ledger Entry", "Donation")
			donation_doc.cancel()
			frappe.msgprint(_("{0} {1} cancelled").format(donation_doc.doctype, donation_doc.name))