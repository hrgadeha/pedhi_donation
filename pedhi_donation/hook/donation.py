import frappe
from erpnext.accounts.party import get_party_account
from frappe import _
from frappe.utils import money_in_words

def autoname(doc, method):
	if frappe.db.get_single_value("Non Profit Settings", "donation_naming_setting") == 'User Choice':
		if not doc.user_choice_name:
			frappe.throw('Please add value in Field <b>User Choice Name</b> to create autoname of this membership')
		else:
			doc.name = doc.user_choice_name

def validate(doc, method):
	validate_repeating_cost_center(doc)
	remove_zero_amount_cost_center(doc)
	calculate_amount(doc)
	auto_generate_remarks(doc)
	update_donor_details(doc)

def validate_repeating_cost_center(doc):
	"""Error when Same Company is entered multiple times in accounts"""
	cost_center_list = []
	for entry in doc.split_cost_center_table:
		cost_center_list.append(entry.cost_center)

		if len(cost_center_list) != len(set(cost_center_list)):
			frappe.throw("<b>{0}</b> Cost Center is entered more than once".format(entry.cost_center))

def remove_zero_amount_cost_center(doc):
	to_remove = [
		d
		for d in doc.split_cost_center_table
		if d.amount == 0
	]

	for d in to_remove:
		doc.remove(d)

def calculate_amount(doc):
	doc.amount = sum(obj.amount for obj in doc.split_cost_center_table)
	doc.in_words = money_in_words(doc.amount)

def auto_generate_remarks(doc):
	mode_of_payment_type = frappe._dict(
		frappe.get_all("Mode of Payment", fields=["name", "type"], as_list=1)
	)
	if doc.mode_of_payment:
		if mode_of_payment_type.get(doc.mode_of_payment) == "Cash":
			create_cash_narration(doc)

		if mode_of_payment_type.get(doc.mode_of_payment) == "Bank":
			create_bank_narration(doc)

def update_donor_details(doc):
	if doc.donor and frappe.db.exists('Donor', doc.donor):
		frappe.db.set_value('Donor', doc.donor, {
			'pan_no' : doc.pan_no,
			'aadhar_no' : doc.aadhar_no,
			'mobile' : doc.mobile,
			'address' : doc.address,
			'upload_pan' : doc.upload_pan,
			'upload_aadhar' : doc.upload_aadhar
		})

def create_cash_narration(doc):
	doc.payment_id = ''
	if doc.name:
		doc.payment_id += '{0} '.format(doc.name)
	if doc.donor_name_for_receipt:
		doc.payment_id += ', {0} '.format(doc.donor_name_for_receipt)
	if doc.remark:
		doc.payment_id += ', {0}'.format(doc.remark)

def create_bank_narration(doc):
	doc.payment_id = ''
	if doc.name:
		doc.payment_id += '{0} '.format(doc.name)
	if doc.cheque_no:
		doc.payment_id += ', {0} '.format(doc.cheque_no)
	if doc.bank:
		doc.payment_id += ', {0} '.format(doc.bank)
	if doc.remark:
		doc.payment_id += ', {0}'.format(doc.remark)

def on_submit(doc, method):
	if doc.amount > 0:
		create_split_cost_center_jv(doc)

def create_split_cost_center_jv(doc):
	jv = frappe.new_doc('Journal Entry')
	jv.company = doc.company
	jv.posting_date = doc.date
	jv.mode_of_payment = doc.mode_of_payment
	jv.donation = doc.name
	jv.cheque_no = doc.cheque_no
	jv.cheque_date = doc.date if doc.cheque_no else ""
	jv.remark = doc.payment_id
	mode_of_payment_type = frappe._dict(
		frappe.get_all("Mode of Payment", fields=["name", "type"], as_list=1)
	)
	jv.voucher_type = "Bank Entry"

	if doc.mode_of_payment and mode_of_payment_type.get(doc.mode_of_payment) == "Cash":
		jv.voucher_type = "Cash Entry"

	party_account = frappe.db.get_value("Company", doc.company, "donor_account")

	payment_account = frappe.db.get_value('Mode of Payment Account', {
		'parent': doc.mode_of_payment,
		'company': doc.company
	},	'default_account')

	mode_of_payment_link = frappe.utils.get_link_to_form("Mode of Payment", doc.mode_of_payment)

	if not party_account:
		frappe.throw('Please Setup party account first in <b>Company Data</b>')

	if not payment_account:
		frappe.throw('Please Setup default mode of payment account first {0}'.format(mode_of_payment_link))

	for d in doc.split_cost_center_table:
		if d.amount > 0:
			jv.append(
				"accounts",
				{
					"account": party_account,
					"credit_in_account_currency": d.amount,
					"party_type": "Donor",
					"party": doc.donor,
					"cost_center": d.cost_center,
					"reference_type": doc.doctype,
					"reference_name": doc.name,
					"user_remarks": d.remarks
				},
			)
			jv.append(
				"accounts",
				{
					"account": payment_account,
					"debit_in_account_currency": d.amount,
					"cost_center": d.cost_center,
				},
			)

	jv.flags.ignore_mandatory = True
	jv.insert()
	doc.db_set('journal_entry', jv.name)
	jv.save()
	jv.submit()
	frappe.msgprint(_("{0} {1} created").format(jv.doctype, jv.name))

def on_trash(doc, method):
	frappe.db.sql("""delete from `tabJournal Entry` where name = '{0}';""".format(doc.journal_entry))
	frappe.db.sql("""delete from `tabGL Entry` where voucher_no = '{0}';""".format(doc.journal_entry))
	frappe.db.sql("""delete from `tabPayment Ledger Entry` where voucher_no = '{0}';""".format(doc.journal_entry))

@frappe.whitelist()
def get_cost_center(company = None):
	if not company:
		frappe.throw('Please Select Company First.')
		return

	return frappe.get_list("Cost Center", {"company": company, 'is_group': 0}, 'name') or []

def on_cancel(doc, method):
	cancel_jv(doc)

def cancel_jv(doc):
	doc.ignore_linked_doctypes = ("GL Entry", "Payment Ledger Entry", "Donation")
	if doc.journal_entry and frappe.db.exists('Journal Entry', doc.journal_entry):
		jv_doc = frappe.get_doc('Journal Entry', doc.journal_entry)
		if jv_doc.docstatus == 1:
			jv_doc.flags.ignore_permissions = True
			jv_doc.ignore_linked_doctypes = ("GL Entry", "Payment Ledger Entry")
			jv_doc.cancel()
			frappe.msgprint(_("{0} {1} cancelled").format(jv_doc.doctype, jv_doc.name))

@frappe.whitelist()
def get_last_vocuher_date():
	last_donation_doc = frappe.get_last_doc('Donation')
	return last_donation_doc.date

@frappe.whitelist()
def fetch_pan_attachment(donor):
    # Fetch the PAN attachment from the Donor doctype
    donor_attachment = frappe.db.get_value('Donor', donor, ['upload_pan','upload_aadhar'], as_dict = True)

    return donor_attachment