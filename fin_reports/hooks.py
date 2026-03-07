app_name = "fin_reports"
app_title = "Financial Reports"
app_publisher = "Your Name"
app_description = "Custom sales reporting by item group"
app_email = "you@example.com"
app_license = "MIT"

after_install  = "fin_reports.fin_reports.setup.create_custom_fields"
after_migrate  = "fin_reports.fin_reports.setup.create_custom_fields"
after_uninstall = "fin_reports.fin_reports.setup.remove_custom_fields"

doc_events = {
    "Sales Invoice": {
        "after_insert": "fin_reports.fin_reports.events.sales_invoice.update_item_group_summary",
        "on_update":    "fin_reports.fin_reports.events.sales_invoice.update_item_group_summary",
        "on_cancel":    "fin_reports.fin_reports.events.sales_invoice.delete_item_group_summary"
    }
}
