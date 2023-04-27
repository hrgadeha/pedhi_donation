import frappe
from non_profit.non_profit.doctype.membership.membership import Membership
from frappe import _

class CustomMembership(Membership):
	def validate(self):
		self.validate_membership_period()
		super(CustomMembership, self).validate()

	def validate_membership_period(self):
		pass