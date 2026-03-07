import frappe
from frappe import _
from frappe.utils import flt, getdate
from erpnext.accounts.report.financial_statements import (
    get_period_list,
    get_data,
    get_columns,
)
from erpnext.accounts.report.utils import get_currency


def execute(filters=None):
    filters = frappe._dict(filters or {})

    # Collect companies from individual dropdowns company_1 to company_4
    companies = []
    for i in range(1, 5):
        c = filters.get(f"company_{i}")
        if c and c.strip() and c.strip() not in companies:
            companies.append(c.strip())

    if not companies:
        frappe.throw(_("Please select at least one company"))

    primary_company   = companies[0]
    filter_based_on   = filters.get("filter_based_on") or "Date Range"
    period_start_date = filters.get("period_start_date")
    period_end_date   = filters.get("period_end_date")
    from_fiscal_year  = filters.get("from_fiscal_year")
    to_fiscal_year    = filters.get("to_fiscal_year")
    periodicity       = filters.get("periodicity") or "Yearly"
    accumulated_values = filters.get("accumulated_values", 1)

    # Build period list from primary company
    period_list = get_period_list(
        from_fiscal_year,
        to_fiscal_year,
        period_start_date,
        period_end_date,
        filter_based_on,
        periodicity,
        accumulated_values=accumulated_values,
        company=primary_company,
    )

    # Build columns — Account + one Total column per company + Grand Total
    columns = [
        {
            "fieldname": "account",
            "label": _("Account"),
            "fieldtype": "Data",
            "width": 280,
        }
    ]

    for company in companies:
        ckey = company.replace(" ", "_")
        columns.append({
            "fieldname": f"total__{ckey}",
            "label": company,
            "fieldtype": "Currency",
            "width": 180,
            "options": "currency",
        })

    if len(companies) > 1:
        columns.append({
            "fieldname": "grand_total",
            "label": _("Grand Total"),
            "fieldtype": "Currency",
            "width": 180,
            "options": "currency",
        })

    # Fetch income and expense data per company
    company_filters = frappe._dict({
        "filter_based_on":   filter_based_on,
        "period_start_date": period_start_date,
        "period_end_date":   period_end_date,
        "from_fiscal_year":  from_fiscal_year,
        "to_fiscal_year":    to_fiscal_year,
        "periodicity":       periodicity,
        "accumulated_values": accumulated_values,
        "include_default_book_entries": filters.get("include_default_book_entries", 1),
    })

    all_income  = {}
    all_expense = {}

    for company in companies:
        company_filters.company = company
        income = get_data(
            company, "Income", "Credit", period_list,
            filters=company_filters,
            accumulated_values=accumulated_values,
            ignore_closing_entries=True,
            ignore_accumulated_values_for_fy=True,
        )
        expense = get_data(
            company, "Expense", "Debit", period_list,
            filters=company_filters,
            accumulated_values=accumulated_values,
            ignore_closing_entries=True,
            ignore_accumulated_values_for_fy=True,
        )
        all_income[company]  = income  or []
        all_expense[company] = expense or []

    # Build merged data rows
    data = build_data(companies, all_income, all_expense, period_list)

    return columns, data


def get_account_map(rows):
    amap = {}
    for row in rows:
        if row and row.get("account"):
            amap[row["account"]] = row
    return amap


def build_data(companies, all_income, all_expense, period_list):
    data = []

    def add_section(root_type, rows_per_company):
        # Collect all unique account keys across all companies
        all_keys = []
        seen = set()
        for company in companies:
            for row in rows_per_company.get(company, []):
                if row and row.get("account") and row["account"] not in seen:
                    # Skip the summary/total rows (last 2)
                    rows = rows_per_company.get(company, [])
                    if row in rows[-2:]:
                        continue
                    seen.add(row["account"])
                    all_keys.append(row["account"])

        for key in all_keys:
            # Get indent and account_name from whichever company has this account
            sample = None
            for company in companies:
                amap = get_account_map(rows_per_company.get(company, []))
                if key in amap:
                    sample = amap[key]
                    break

            if not sample:
                continue

            merged = {
                "account":        key,
                "account_name":   sample.get("account_name", key),
                "parent_account": sample.get("parent_account"),
                "indent":         sample.get("indent", 1),
                "is_group":       sample.get("is_group", 0),
                "grand_total":    0,
                "currency":       sample.get("currency"),
            }

            for company in companies:
                ckey = company.replace(" ", "_")
                merged[f"total__{ckey}"] = 0

            for company in companies:
                ckey = company.replace(" ", "_")
                amap = get_account_map(rows_per_company.get(company, []))
                row  = amap.get(key)

                if row:
                    total = flt(row.get("total")) or 0
                    merged[f"total__{ckey}"] = total
                    merged["grand_total"]   += total

            data.append(merged)

    # INCOME SECTION
    income_header = {
        "account": _("Income"), "account_name": _("Income"),
        "indent": 0, "is_group": 1, "grand_total": 0,
    }
    for company in companies:
        income_header[f"total__{company.replace(' ', '_')}"] = 0
    data.append(income_header)

    add_section("Income", all_income)

    income_total = {
        "account": _("Total Income"), "account_name": _("Total Income"),
        "indent": 0, "is_group": 1, "bold": 1, "grand_total": 0,
    }
    for company in companies:
        ckey  = company.replace(" ", "_")
        rows  = all_income.get(company, [])
        total = flt(rows[-2].get("total")) if len(rows) >= 2 else 0
        income_total[f"total__{ckey}"] = total
        income_total["grand_total"]   += total
    data.append(income_total)
    data.append({})

    # EXPENSE SECTION
    expense_header = {
        "account": _("Expense"), "account_name": _("Expense"),
        "indent": 0, "is_group": 1, "grand_total": 0,
    }
    for company in companies:
        expense_header[f"total__{company.replace(' ', '_')}"] = 0
    data.append(expense_header)

    add_section("Expense", all_expense)

    expense_total = {
        "account": _("Total Expense"), "account_name": _("Total Expense"),
        "indent": 0, "is_group": 1, "bold": 1, "grand_total": 0,
    }
    for company in companies:
        ckey  = company.replace(" ", "_")
        rows  = all_expense.get(company, [])
        total = flt(rows[-2].get("total")) if len(rows) >= 2 else 0
        expense_total[f"total__{ckey}"] = total
        expense_total["grand_total"]   += total
    data.append(expense_total)
    data.append({})

    # NET PROFIT ROW
    net_profit_row = {
        "account": _("Net Profit / Loss"), "account_name": _("Net Profit / Loss"),
        "indent": 0, "is_group": 1, "warn_if_negative": True, "grand_total": 0,
    }
    for company in companies:
        ckey      = company.replace(" ", "_")
        inc_rows  = all_income.get(company, [])
        exp_rows  = all_expense.get(company, [])
        inc_total = flt(inc_rows[-2].get("total")) if len(inc_rows) >= 2 else 0
        exp_total = flt(exp_rows[-2].get("total")) if len(exp_rows) >= 2 else 0
        net       = inc_total - exp_total
        net_profit_row[f"total__{ckey}"] = net
        net_profit_row["grand_total"]   += net
    data.append(net_profit_row)

    return data
