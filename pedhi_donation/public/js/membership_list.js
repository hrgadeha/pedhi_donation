frappe.listview_settings['Membership'] = {
	get_indicator: function(doc) {
		if (doc.membership_status == 'New') {
			return [__('New'), 'blue', 'membership_status,=,New'];
		} else if (doc.membership_status === 'Current') {
			return [__('Current'), 'green', 'membership_status,=,Current'];
		} else if (doc.membership_status === 'Pending') {
			return [__('Pending'), 'yellow', 'membership_status,=,Pending'];
		} else if (doc.membership_status === 'Expired') {
			return [__('Expired'), 'grey', 'membership_status,=,Expired'];
		} else if (doc.membership_status === 'Paid') {
			return [__('Paid'), 'green', 'membership_status,=,Paid'];
		} else if (doc.membership_status === 'Unpaid') {
			return [__('Unpaid'), 'orange', 'membership_status,=,Unpaid'];
		} else {
			return [__('Cancelled'), 'red', 'membership_status,=,Cancelled'];
		}
	}
};