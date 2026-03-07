import frappe

def execute(filters=None):
    filters = filters or {}

    columns = [
        {
            "label": "Item Group",
            "fieldname": "item_group",
            "fieldtype": "Link",
            "options": "Item Group",
            "width": 180
        },
        {
            "label": "Quantity",
            "fieldname": "total_qty",
            "fieldtype": "Float",
            "width": 140
        },
        {
            "label": "Total Amount",
            "fieldname": "total_amount",
            "fieldtype": "Currency",
            "width": 180
        },
        {
            "label": "Margin",
            "fieldname": "total_margin",
            "fieldtype": "Currency",
            "width": 160
        },
        {
            "label": "Average Margin",
            "fieldname": "avg_margin",
            "fieldtype": "Currency",
            "width": 160
        },
        {
            "label": "Invoices",
            "fieldname": "invoice_count",
            "fieldtype": "Int",
            "width": 110
        }
    ]

    conditions = "WHERE 1=1"
    values = {}

    if filters.get("from_date"):
        conditions += " AND posting_date >= %(from_date)s"
        values["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        conditions += " AND posting_date <= %(to_date)s"
        values["to_date"] = filters["to_date"]

    if filters.get("customer"):
        conditions += " AND customer = %(customer)s"
        values["customer"] = filters["customer"]

    if filters.get("item_group"):
        conditions += " AND item_group = %(item_group)s"
        values["item_group"] = filters["item_group"]

    data = frappe.db.sql(f"""
        SELECT
            item_group,
            SUM(total_qty)                                 AS total_qty,
            SUM(total_amount)                              AS total_amount,
            SUM(total_margin)                              AS total_margin,
            SUM(total_margin) / NULLIF(SUM(total_qty), 0) AS avg_margin,
            COUNT(DISTINCT sales_invoice)                  AS invoice_count
        FROM
            `tabItem Group Sales Summary`
        {conditions}
        GROUP BY
            item_group
        ORDER BY
            total_amount DESC
    """, values, as_dict=True)

    return columns, data
