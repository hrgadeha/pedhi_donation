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

		jv_debit = {}
		jv_debit.update({
			"unique_id" : unique_id,
			"base_vch_type": 'Receipt',
			"vocuher_type": 'Receipt',
			"vch_no": jv.donation,
			"vch_date": jv.posting_date,
			"ledger": jv.account,
			"debit": jv.debit,
			"credit": 0,
			"narration": jv.cheque_no,
			"cost_category": "",
			"cost_center": "",
			"cost_center_debit": jv.debit,
			"cost_center_credit": 0,
		})

		data.append(jv_debit)

		if jv.name:
			jv_doc_data = frappe.get_doc('Journal Entry', jv.name)
			for acc in jv_doc_data.accounts:
				if acc.credit > 0:
					jv_credit = {}
					jv_credit.update({
						"unique_id" : unique_id,
						"base_vch_type": 'Receipt',
						"vocuher_type": 'Receipt',
						"vch_no": jv_doc_data.donation,
						"vch_date": jv_doc_data.posting_date,
						"ledger": acc.account,
						"debit": 0,
						"credit": acc.credit,
						"narration": jv_doc_data.cheque_no,
						"cost_category": "primary cost category",
						"cost_center": acc.cost_center,
						"cost_center_debit": 0,
						"cost_center_credit": acc.credit,
					})

					data.append(jv_credit)
			
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
			jv_doc.name,
			jv_doc.donation,
			jv_doc.posting_date,
			jv_doc_account.account,
			Sum(jv_doc_account.debit).as_("debit"),
			jv_doc.cheque_no
		)
		.where(
			(jv_doc.donation != "" or jv_doc.donation != None) 
			& (jv_doc.docstatus == 1)
			& (jv_doc_account.debit > 0)
		)
		.groupby(jv_doc.name)
		.groupby(jv_doc_account.account)
		.orderby(jv_doc.donation)
		.orderby(jv_doc_account.account)
	)

	if filters.get('company'):
		query = query.where(jv_doc.company == filters.get('company'))

	if filters.get('from_date') and filters.get('to_date'):
		query = query.where(jv_doc.posting_date.between(filters.get("from_date"), filters.get("to_date")))

	return query.run(as_dict=True)