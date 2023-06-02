import frappe
from erpnext.accounts.party import get_party_account
from frappe import _
from frappe.utils import getdate
from frappe.utils import money_in_words

def autoname(doc, method):
	if frappe.db.get_single_value("Non Profit Settings", "membership_naming_setting") == 'User Choice':
		if not doc.user_choice_name:
			frappe.throw('Please add value in Field <b>User Choice Name</b> to create autoname of this membership')
		else:
			doc.name = doc.user_choice_name

def validate(doc, method):
	validate_amount(doc)
	validate_repeating_cost_center(doc)
	remove_zero_amount_cost_center(doc)
	calculate_amount(doc)
	auto_generate_remarks(doc)

def validate_amount(doc):
	if doc.amount <= 0:
		frappe.throw('Amount can not be 0.')

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

def create_cash_narration(doc):
	doc.payment_id = ''
	if doc.name:
		doc.payment_id += '{0} '.format(doc.name)
	if doc.member_name:
		doc.payment_id += ', {0} '.format(doc.member_name)
	if doc.remarks:
		doc.payment_id += ', {0}'.format(doc.remarks)

def create_bank_narration(doc):
	doc.payment_id = ''
	if doc.name:
		doc.payment_id += '{0} '.format(doc.name)
	if doc.chque_no:
		doc.payment_id += ', {0} '.format(doc.chque_no)
	if doc.bank:
		doc.payment_id += ', {0} '.format(doc.bank)
	if doc.remarks:
		doc.payment_id += ', {0}'.format(doc.remarks)

@frappe.whitelist()
def get_membership_cost_Center(company = None, membership_type = None):
	if not company:
		frappe.throw('Please Select Company First.')
		return

	if not membership_type:
		frappe.throw('Please Select Membership Type First.')
		return

	return frappe.get_list("Split Cost Center Table", {"company": company, 'parent': membership_type}, 
		['cost_center', 'company', 'amount'], ignore_permissions = True) or []

@frappe.whitelist()
def create_split_cost_center_jv(membership_id):
	mem_doc = frappe.get_doc('Membership', membership_id)
	if not mem_doc:
		return

	jv = frappe.new_doc('Journal Entry')
	jv.company = mem_doc.company
	jv.posting_date = getdate(mem_doc.date)
	jv.mode_of_payment = mem_doc.mode_of_payment
	jv.membership = mem_doc.name
	jv.cheque_no = mem_doc.chque_no
	jv.cheque_date = getdate(mem_doc.chque_date) if mem_doc.chque_no else ""
	jv.remark = mem_doc.payment_id
	mode_of_payment_type = frappe._dict(
		frappe.get_all("Mode of Payment", fields=["name", "type"], as_list=1)
	)
	jv.voucher_type = "Bank Entry"

	if mem_doc.mode_of_payment and mode_of_payment_type.get(mem_doc.mode_of_payment) == "Cash":
		jv.voucher_type = "Cash Entry"

	party_account = frappe.db.get_value("Company", mem_doc.company, "member_account")

	payment_account = frappe.db.get_value('Mode of Payment Account', {
		'parent': mem_doc.mode_of_payment,
		'company': mem_doc.company
	},	'default_account')

	mode_of_payment_link = frappe.utils.get_link_to_form("Mode of Payment", mem_doc.mode_of_payment)

	if not party_account:
		frappe.throw('Please Setup party account first in <b>Company Data</b>')

	if not payment_account:
		frappe.throw('Please Setup default mode of payment account first {0}'.format(mode_of_payment_link))

	for d in mem_doc.split_cost_center_table:
		if d.amount > 0:
			jv.append(
				"accounts",
				{
					"account": party_account,
					"credit_in_account_currency": d.amount,
					"party_type": "Member",
					"party": mem_doc.member,
					"cost_center": d.cost_center,
					"reference_type": mem_doc.doctype,
					"reference_name": mem_doc.name,
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
	mem_doc.db_set('journal_entry', jv.name)
	mem_doc.db_set('membership_status', 'Paid')
	jv.save()
	jv.submit()
	frappe.msgprint(_("{0} {1} created").format(jv.doctype, jv.name))
	update_member_status(mem_doc)

@frappe.whitelist()
def cancel_journal_entry(membership_id):
	mem_doc = frappe.get_doc('Membership', membership_id)
	if not mem_doc:
		return

	mem_doc.ignore_linked_doctypes = ("GL Entry", "Payment Ledger Entry", "Donation", "Membership")
	if mem_doc.journal_entry and frappe.db.exists('Journal Entry', mem_doc.journal_entry):
		jv_doc = frappe.get_doc('Journal Entry', mem_doc.journal_entry)
		if jv_doc.docstatus == 1:
			jv_doc.flags.ignore_permissions = True
			jv_doc.ignore_linked_doctypes = ("GL Entry", "Payment Ledger Entry")
			jv_doc.cancel()
			frappe.msgprint(_("{0} {1} cancelled").format(jv_doc.doctype, jv_doc.name))

	mem_doc.db_set('journal_entry', None)
	mem_doc.db_set('membership_status', 'Unpaid')
	update_member_status(mem_doc)

def update_member_status(mem_doc):
	membership_doc = frappe.get_last_doc('Membership', filters={"member": mem_doc.member})
	if membership_doc.member and frappe.db.exists('Member', membership_doc.member):
		frappe.db.set_value('Member', membership_doc.member, {
			'status' : membership_doc.membership_status,
			'lr_no' : membership_doc.name,
			'lr_date' : membership_doc.date
		})

def set_expired_status():
	frappe.db.sql("""
		UPDATE
			`tabMembership` SET `membership_status` = 'Expired'
		WHERE
			`membership_status` not in ('Cancelled') AND `to_date` < %s
		""", (getdate()))

def set_status_for_member():
	all_member = frappe.db.get_all('Member', ['name', 'status'])
	for member in all_member:
		if frappe.db.exists('Member', member.name) and frappe.db.exists('Membership', {"member": member.name}):
			membership_doc = frappe.get_last_doc('Membership', {"member": member.name})
			if membership_doc and member.status != membership_doc.membership_status:
				frappe.db.set_value('Member', member.name, {
					'status' : membership_doc.membership_status,
					'lr_no' : membership_doc.name,
					'lr_date' : membership_doc.date
				})

@frappe.whitelist()
def get_last_vocuher_date():
	last_membership_doc = frappe.get_last_doc('Membership')
	return last_membership_doc.date