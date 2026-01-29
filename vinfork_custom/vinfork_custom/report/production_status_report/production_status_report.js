frappe.query_reports["Production Status Report"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "width": "80"
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "width": "80"
        }
    ],
    "formatter": function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        // Logic for Overall Status
        if (column.fieldname == "overall_status") {
            if (value == "Completed" || value == "Ready") {
                value = "<span style='color:green; font-weight:bold'>" + value + "</span>";
            } else if (value == "WIP") {
                value = "<span style='color:orange; font-weight:bold'>" + value + "</span>";
            } else if (value == "Not Started" || value == "NYS") {
                value = "<span style='color:red'>" + value + "</span>";
            }
        }

        // Logic for Dynamic Operation Columns (ending in _status)
        else if (column.fieldname && column.fieldname.endsWith("_status")) {
            if (value == "Done") {
                value = "<span style='color:green; font-weight:bold'>" + value + "</span>";
            } else if (value == "WIP" || value == "In Prog") {
                value = "<span style='color:orange; font-weight:bold'>" + value + "</span>";
            } else if (value == "Not Started") {
                value = "<span style='color:gray'>" + value + "</span>";
            }
        }

        return value;
    }
};
