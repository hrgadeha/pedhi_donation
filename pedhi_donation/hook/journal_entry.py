import frappe
from frappe import _
from frappe.utils import getdate

def validate(doc, method):
	if not doc.donation or doc.membership:
		if doc.voucher_type == 'Bank Entry':
			bank_jv_narration(doc)

		if doc.voucher_type == 'Cash Entry':
			cash_jv_narration(doc)

def bank_jv_narration(doc):
	doc.remark = ''
	if doc.cheque_no:
		doc.remark += '{0} '.format(doc.cheque_no)
	if doc.cheque_date:
		doc.remark += ': {0} '.format(frappe.utils.formatdate(doc.cheque_date, "dd-MM-YYYY"))
	if doc.user_remark:
		doc.remark += ': {0} '.format(doc.user_remark)

def cash_jv_narration(doc):
	doc.remark = ''
	if doc.user_remark:
		doc.remark += '{0}'.format(doc.user_remark)

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