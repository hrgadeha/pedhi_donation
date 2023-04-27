import frappe
from erpnext.accounts.party import get_party_account
from frappe import _

def validate(doc, method):
	validate_repeating_cost_center(doc)
	remove_zero_amount_cost_center(doc)
	calculate_amount(doc)

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