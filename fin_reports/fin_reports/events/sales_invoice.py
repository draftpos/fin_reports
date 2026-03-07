import frappe

def update_item_group_summary(doc, method=None):

    # Step 1: Update margin fields on each item row
    for item in doc.items:
        incoming = item.incoming_rate or 0
        rate     = item.rate or 0
        qty      = item.qty or 0

        margin_amount  = (rate - incoming) * qty
        margin_percent = ((rate - incoming) / rate * 100) if rate else 0

        frappe.db.set_value(
            "Sales Invoice Item",
            item.name,
            {
                "margin_amount":  margin_amount,
                "margin_percent": margin_percent
            },
            update_modified=False
        )

    # Step 2: Delete old summary records for this invoice
    frappe.db.delete("Item Group Sales Summary", {
        "sales_invoice": doc.name
    })

    # Step 3: Group items by item_group
    group_totals = {}
    for item in doc.items:
        group    = item.item_group or "Uncategorized"
        incoming = item.incoming_rate or 0
        rate     = item.rate or 0
        qty      = item.qty or 0

        item_margin = (rate - incoming) * qty

        if group not in group_totals:
            group_totals[group] = {
                "total_qty":    0,
                "total_amount": 0,
                "total_margin": 0,
                "item_count":   0
            }

        group_totals[group]["total_qty"]    += qty
        group_totals[group]["total_amount"] += item.amount or 0
        group_totals[group]["total_margin"] += item_margin
        group_totals[group]["item_count"]   += 1

    # Step 4: Insert summary records
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
