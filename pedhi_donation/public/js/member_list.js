frappe.listview_settings['Member'] = {
	get_indicator: function(doc) {
		if (doc.status == 'New') {
			return [__('New'), 'blue', 'status,=,New'];
		} else if (doc.status === 'Unpaid') {
			return [__('Unpaid'), 'yellow', 'status,=,Unpaid'];
		} else if (doc.status === 'Paid') {
			return [__('Paid'), 'green', 'status,=,Paid'];
		} else if (doc.status === 'Expired') {
			return [__('Expired'), 'red', 'status,=,Expired'];
		}
	}
};
