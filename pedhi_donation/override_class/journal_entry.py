import frappe
from erpnext.accounts.doctype.journal_entry.journal_entry import JournalEntry
from frappe import _

class CustomJournalEntry(JournalEntry):
	def validate(self):
		self.create_remarks()
		super(CustomJournalEntry, self).validate()

	def create_remarks(self):
		pass