app_name = "fin_reports"
app_title = "Financial Reports"
app_publisher = "Your Name"
app_description = "Custom sales reporting by item group"
app_email = "you@example.com"
app_license = "MIT"

doc_events = {
    "Sales Invoice": {
        "after_insert": "fin_reports.fin_reports.events.sales_invoice.update_item_group_summary",
        "on_update":    "fin_reports.fin_reports.events.sales_invoice.update_item_group_summary",
        "on_cancel":    "fin_reports.fin_reports.events.sales_invoice.delete_item_group_summary"
    }
}
