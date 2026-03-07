import frappe

def execute(filters=None):
    filters = filters or {}

    columns = [
        {
            "label": "Item Group",
            "fieldname": "item_group",
            "fieldtype": "Link",
            "options": "Item Group",
            "width": 200
        },
        {
            "label": "Total Quantity Sold",
            "fieldname": "total_qty",
            "fieldtype": "Float",
            "width": 180
        },
        {
            "label": "Total Amount Sold",
            "fieldname": "total_amount",
            "fieldtype": "Currency",
            "width": 200
        },
        {
            "label": "Number of Invoices",
            "fieldname": "invoice_count",
            "fieldtype": "Int",
            "width": 160
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

    data = frappe.db.sql(f"""
        SELECT
            item_group,
            SUM(total_qty)                  AS total_qty,
            SUM(total_amount)               AS total_amount,
            COUNT(DISTINCT sales_invoice)   AS invoice_count
        FROM
            `tabItem Group Sales Summary`
        {conditions}
        GROUP BY
            item_group
        ORDER BY
            total_amount DESC
    """, values, as_dict=True)

    return columns, data
