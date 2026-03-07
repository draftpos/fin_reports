import frappe

def update_item_group_summary(doc, method=None):

    # Update margin fields on each item row
    for item in doc.items:
        incoming = item.incoming_rate or 0
        rate     = item.rate or 0
        qty      = item.qty or 0

        # Margin = (rate - incoming_rate) * qty
        margin_amount  = (rate - incoming) * qty
        # Margin % = incoming_rate / rate * 100
        margin_percent = (incoming / rate * 100) if rate else 0

        frappe.db.set_value(
            "Sales Invoice Item", item.name,
            {"margin_amount": margin_amount, "margin_percent": margin_percent},
            update_modified=False
        )

    # Delete old summary records
    frappe.db.delete("Item Group Sales Summary", {"sales_invoice": doc.name})

    # Get cost center from invoice or first item
    cost_center = doc.cost_center if hasattr(doc, "cost_center") and doc.cost_center else (
        doc.items[0].cost_center if doc.items else None
    )

    # Group items by item_group
    group_totals = {}
    for item in doc.items:
        group    = item.item_group or "Uncategorized"
        incoming = item.incoming_rate or 0
        rate     = item.rate or 0
        qty      = item.qty or 0

        # Margin per item = (rate - incoming_rate) * qty
        item_margin         = (rate - incoming) * qty
        item_margin_percent = (incoming / rate * 100) if rate else 0

        if group not in group_totals:
            group_totals[group] = {
                "total_qty":            0,
                "total_amount":         0,
                "total_margin":         0,
                "total_margin_percent": 0,
                "item_count":           0
            }

        group_totals[group]["total_qty"]            += qty
        group_totals[group]["total_amount"]         += item.amount or 0
        group_totals[group]["total_margin"]         += item_margin
        group_totals[group]["total_margin_percent"] += item_margin_percent
        group_totals[group]["item_count"]           += 1

    # Insert summary records
    for group_name, values in group_totals.items():
        item_count         = values["item_count"]
        avg_margin_percent = values["total_margin_percent"] / item_count if item_count else 0

        frappe.get_doc({
            "doctype":            "Item Group Sales Summary",
            "sales_invoice":      doc.name,
            "posting_date":       doc.posting_date,
            "company":            doc.company,
            "cost_center":        cost_center,
            "customer":           doc.customer,
            "item_group":         group_name,
            "total_qty":          values["total_qty"],
            "total_amount":       values["total_amount"],
            "total_margin":       values["total_margin"],
            "avg_margin_percent": avg_margin_percent
        }).insert(ignore_permissions=True)

    frappe.db.commit()


def delete_item_group_summary(doc, method=None):
    frappe.db.delete("Item Group Sales Summary", {"sales_invoice": doc.name})
    frappe.db.commit()
