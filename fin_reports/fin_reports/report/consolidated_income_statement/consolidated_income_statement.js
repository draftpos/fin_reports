frappe.query_reports["Consolidated Income Statement"] = {
    tree: true,
    name_field: "account",
    parent_field: "parent_account",
    initial_depth: 3,
    formatter: function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        if (data && !data.parent_account) {
            value = $(`<span>${value}</span>`);
            var $value = $(value).css("font-weight", "bold");
            if (data.warn_if_negative && data[column.fieldname] < 0) {
                $value.addClass("text-danger");
            }
            value = $value.wrap("<p></p>").parent().html();
        }
        return value;
    },
    filters: [
        {
            fieldname: "company_1",
            label: __("Company 1"),
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_default("company"),
            reqd: 1
        },
        {
            fieldname: "company_2",
            label: __("Company 2"),
            fieldtype: "Link",
            options: "Company",
            reqd: 0
        },
        {
            fieldname: "company_3",
            label: __("Company 3"),
            fieldtype: "Link",
            options: "Company",
            reqd: 0
        },
        {
            fieldname: "company_4",
            label: __("Company 4"),
            fieldtype: "Link",
            options: "Company",
            reqd: 0
        },
        {
            fieldname: "filter_based_on",
            label: __("Filter Based On"),
            fieldtype: "Select",
            options: "Date Range\nFiscal Year",
            default: "Date Range",
            reqd: 1,
            on_change: function() {
                let filter_based_on = frappe.query_report.get_filter_value("filter_based_on");
                if (filter_based_on === "Date Range") {
                    frappe.query_report.toggle_filter_display("period_start_date", false);
                    frappe.query_report.toggle_filter_display("period_end_date", false);
                    frappe.query_report.toggle_filter_display("from_fiscal_year", true);
                    frappe.query_report.toggle_filter_display("to_fiscal_year", true);
                } else {
                    frappe.query_report.toggle_filter_display("period_start_date", false);
                    frappe.query_report.toggle_filter_display("period_end_date", false);
                    frappe.query_report.toggle_filter_display("from_fiscal_year", false);
                    frappe.query_report.toggle_filter_display("to_fiscal_year", false);
                }
            }
        },
        {
            fieldname: "period_start_date",
            label: __("Start Date"),
            fieldtype: "Date",
            default: frappe.datetime.year_start(),
            reqd: 0
        },
        {
            fieldname: "period_end_date",
            label: __("End Date"),
            fieldtype: "Date",
            default: frappe.datetime.year_end(),
            reqd: 0
        },
        {
            fieldname: "from_fiscal_year",
            label: __("From Fiscal Year"),
            fieldtype: "Link",
            options: "Fiscal Year",
            hidden: 1
        },
        {
            fieldname: "to_fiscal_year",
            label: __("To Fiscal Year"),
            fieldtype: "Link",
            options: "Fiscal Year",
            hidden: 1
        },
        {
            fieldname: "periodicity",
            label: __("Periodicity"),
            fieldtype: "Select",
            options: "Yearly\nHalf-Yearly\nQuarterly\nMonthly",
            default: "Yearly",
            reqd: 1
        },
        {
            fieldname: "accumulated_values",
            label: __("Accumulated Values"),
            fieldtype: "Check",
            default: 1
        }
    ]
};
