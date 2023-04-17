from . import __version__ as app_version

app_name = "pedhi_donation"
app_title = "Pedhi Donation"
app_publisher = "Hardik Gadesha"
app_description = "App to Manage Amount split into cost center"
app_email = "hardikgadesha@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/pedhi_donation/css/pedhi_donation.css"
# app_include_js = "/assets/pedhi_donation/js/pedhi_donation.js"

# include js, css files in header of web template
# web_include_css = "/assets/pedhi_donation/css/pedhi_donation.css"
# web_include_js = "/assets/pedhi_donation/js/pedhi_donation.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "pedhi_donation/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Donation" : "public/js/donation.js",
    "Non Profit Settings" : "public/js/non_profit_settings.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "pedhi_donation.utils.jinja_methods",
#	"filters": "pedhi_donation.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "pedhi_donation.install.before_install"
# after_install = "pedhi_donation.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "pedhi_donation.uninstall.before_uninstall"
# after_uninstall = "pedhi_donation.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "pedhi_donation.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Donation": {
		"validate": "pedhi_donation.hook.donation.validate",
		"on_submit": "pedhi_donation.hook.donation.on_submit",
		"on_cancel": "pedhi_donation.hook.donation.on_cancel",
	},
	"Journal Entry": {
		"on_cancel": "pedhi_donation.hook.journal_entry.on_cancel",
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"pedhi_donation.tasks.all"
#	],
#	"daily": [
#		"pedhi_donation.tasks.daily"
#	],
#	"hourly": [
#		"pedhi_donation.tasks.hourly"
#	],
#	"weekly": [
#		"pedhi_donation.tasks.weekly"
#	],
#	"monthly": [
#		"pedhi_donation.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "pedhi_donation.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "pedhi_donation.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "pedhi_donation.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]


# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"pedhi_donation.auth.validate"
# ]

fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "Pedhi Donation"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "Pedhi Donation"]]},
]