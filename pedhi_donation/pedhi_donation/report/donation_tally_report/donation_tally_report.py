# Copyright (c) 2023, Goldsetu and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.query_builder.functions import Sum


def execute(filters=None):
	donation_entry = get_jv_entries(filters)
	columns = get_column()
	data = []

	unique_id = 0
	donation_list = []

	for jv in donation_entry:
		if jv.donation not in donation_list:
			unique_id += 1
			donation_list.append(jv.donation)

		jv.update({
			"unique_id" : unique_id,
			"base_vch_type": 'Receipt',
			"vocuher_type": 'Receipt',
			"vch_no": jv.donation,
			"vch_date": jv.posting_date,
			"ledger": jv.account,
			"debit": jv.debit,
			"credit": jv.credit,
			"cost_center_debit": jv.debit,
			"cost_center_credit": jv.credit,
			"narration": jv.cheque_no,
		})

		if jv.debit > 0:
			jv.update({
				"cost_category": "",
				"cost_center": "",
			})

		else:
			jv.update({
				"cost_category": 'primary cost category',
				"cost_center": jv.cost_center,
			})

		data.append(jv)
			
	return columns, data

def get_column():
	columns = [
		{"label": _("UNIQUE ID"), "fieldname": "unique_id", "fieldtype": "Int", "width": 100},
		{"label": _("BASE VCH-TYPE"), "fieldname": "base_vch_type", "fieldtype": "Data", "width": 100},
		{"label": _("VOUCHER TYPE"), "fieldname": "vocuher_type", "fieldtype": "Data", "width": 140},
		{"label": _("VCH NO"), "fieldname": "vch_no", "fieldtype": "Link", "options": "Donation", "width": 190},
		{"label": _("VCH DATE"), "fieldname": "vch_date", "fieldtype": "Date","width": 120},
		{"label": _("LEDGER"), "fieldname": "ledger", "fieldtype": "Link", "options": "Account", "width": 140},
		{"label": _("DEBIT"), "fieldname": "debit", "fieldtype": "Currency", "width": 140},
		{"label": _("CREDIT"), "fieldname": "credit", "fieldtype": "Currency", "width": 160},
		{"label": _("COST CATEGORY"), "fieldname": "cost_category", "fieldtype": "Data", "width": 160},
		{"label": _("COST CENTRE"), "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "width": 150},
		{"label": _("DEBIT"), "fieldname": "cost_center_debit", "fieldtype": "Currency", "width": 150},
		{"label": _("CREDIT"), "fieldname": "cost_center_credit", "fieldtype": "Currency", "width": 130},
		{"label": _("NARRATION"), "fieldname": "narration", "fieldtype": "Data", "width": 200},
	]

	return columns

def get_jv_entries(filters):
	jv_doc = frappe.qb.DocType("Journal Entry")
	jv_doc_account = frappe.qb.DocType("Journal Entry Account")
	query = (
		frappe.qb.from_(jv_doc)
		.left_join(jv_doc_account)
		.on(jv_doc_account.parent == jv_doc.name)
		.select(
			jv_doc.donation,
			jv_doc.posting_date,
			jv_doc_account.account,
			Sum(jv_doc_account.debit).as_("debit"),
			jv_doc_account.credit,
			jv_doc_account.cost_center,
			jv_doc.cheque_no
		)
		.where(
			(jv_doc.donation != "" or jv_doc.donation != None) 
			& (jv_doc.docstatus == 1)
		)
		.groupby(jv_doc_account.parent)
		.groupby(jv_doc_account.account)
		.groupby(jv_doc_account.credit)
		.orderby(jv_doc.donation)
		.orderby(jv_doc_account.account)
	)

	if filters.get('company'):
		query = query.where(jv_doc.company == filters.get('company'))

	if filters.get('from_date') and filters.get('to_date'):
		query = query.where(jv_doc.posting_date.between(filters.get("from_date"), filters.get("to_date")))

	return query.run(as_dict=True)