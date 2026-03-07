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
            "width": 120
        },
        {
            "label": "Total Amount",
            "fieldname": "total_amount",
            "fieldtype": "Currency",
            "width": 160
        },
        {
            "label": "Margin",
            "fieldname": "total_margin",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": "Average Margin %",
            "fieldname": "avg_margin_percent",
            "fieldtype": "Percent",
            "width": 150
        },
        {
            "label": "Invoices",
            "fieldname": "invoice_count",
            "fieldtype": "Int",
            "width": 100
        }
    ]

    conditions = "WHERE 1=1"
    values = {}

    if filters.get("company"):
        conditions += " AND company = %(company)s"
        values["company"] = filters["company"]

    if filters.get("cost_center"):
        conditions += " AND cost_center = %(cost_center)s"
        values["cost_center"] = filters["cost_center"]

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
            SUM(total_qty)                                                      AS total_qty,
            SUM(total_amount)                                                   AS total_amount,
            SUM(total_margin)                                                   AS total_margin,
            (SUM(avg_margin_percent) / NULLIF(COUNT(sales_invoice), 0))        AS avg_margin_percent,
            COUNT(DISTINCT sales_invoice)                                       AS invoice_count
        FROM
            `tabItem Group Sales Summary`
        {conditions}
        GROUP BY
            item_group
        ORDER BY
            total_amount DESC
    """, values, as_dict=True)

    return columns, data
