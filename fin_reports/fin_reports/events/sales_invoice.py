import frappe

def update_item_group_summary(doc, method=None):
    # Delete old summary records for this invoice
    frappe.db.delete("Item Group Sales Summary", {
        "sales_invoice": doc.name
    })

    # Group items by item_group
    group_totals = {}
    for item in doc.items:
        group = item.item_group or "Uncategorized"
        if group not in group_totals:
            group_totals[group] = {
                "total_qty":        0,
                "total_amount":     0,
                "total_margin":     0,
                "item_count":       0
            }

        # margin per item = (rate - incoming_rate) * qty
        incoming = item.incoming_rate or 0
        item_margin = (item.rate - incoming) * (item.qty or 0)

        group_totals[group]["total_qty"]        += item.qty or 0
        group_totals[group]["total_amount"]     += item.amount or 0
        group_totals[group]["total_margin"]     += item_margin
        group_totals[group]["item_count"]       += 1

    # Insert one record per group
    for group_name, values in group_totals.items():
        item_count = values["item_count"]
        avg_margin = values["total_margin"] / item_count if item_count else 0

        frappe.get_doc({
            "doctype":       "Item Group Sales Summary",
            "sales_invoice": doc.name,
            "posting_date":  doc.posting_date,
            "customer":      doc.customer,
            "item_group":    group_name,
            "total_qty":     values["total_qty"],
            "total_amount":  values["total_amount"],
            "total_margin":  values["total_margin"],
            "avg_margin":    avg_margin
        }).insert(ignore_permissions=True)

    frappe.db.commit()


def delete_item_group_summary(doc, method=None):
    frappe.db.delete("Item Group Sales Summary", {
        "sales_invoice": doc.name
    })
    frappe.db.commit()
