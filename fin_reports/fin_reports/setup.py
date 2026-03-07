import frappe

def create_custom_fields():
    # Margin = rate - incoming_rate
    if not frappe.db.exists("Custom Field", "Sales Invoice Item-margin_amount"):
        frappe.get_doc({
            "doctype":        "Custom Field",
            "dt":             "Sales Invoice Item",
            "fieldname":      "margin_amount",
            "label":          "Margin",
            "fieldtype":      "Currency",
            "insert_after":   "amount",
            "read_only":      1,
            "in_list_view":   1,
            "print_hide":     0,
            "allow_on_submit": 1
        }).insert(ignore_permissions=True)

    # Margin % = (rate - incoming_rate) / rate * 100
    if not frappe.db.exists("Custom Field", "Sales Invoice Item-margin_percent"):
        frappe.get_doc({
            "doctype":        "Custom Field",
            "dt":             "Sales Invoice Item",
            "fieldname":      "margin_percent",
            "label":          "Margin %",
            "fieldtype":      "Percent",
            "insert_after":   "margin_amount",
            "read_only":      1,
            "in_list_view":   1,
            "print_hide":     0,
            "allow_on_submit": 1
        }).insert(ignore_permissions=True)

    frappe.db.commit()
    print("Custom fields created!")


def remove_custom_fields():
    for fieldname in ["Sales Invoice Item-margin_amount", "Sales Invoice Item-margin_percent"]:
        if frappe.db.exists("Custom Field", fieldname):
            frappe.delete_doc("Custom Field", fieldname, ignore_permissions=True)
    frappe.db.commit()
    print("Custom fields removed!")
