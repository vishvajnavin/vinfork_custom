// Logic for Quotation and Sales Order
// Filtering 'leather_colour' field in the items table

var filter_leather_items = function (frm, cdt, cdn) {
    var row = locals[cdt][cdn];

    // Excluded Item Groups
    // Note: If an item is in a sub-group of "Raw Material" (like "Bloom"), check if "Raw Material" filter excludes it.
    // ERPNext query usually checks `item_group`.
    // We can filter by "NOT IN" specific groups if possible, or filter by a property.
    // simpler: Filter by "is_stock_item": 1 and maybe exclude top-level categories if possible.
    // Or just query: Item Group NOT IN [...]

    var excluded_groups = ["Raw Material", "Chairs", "Sofas", "Beds", "Furniture", "Tables"];

    frm.set_query("leather_colour", "items", function () {
        return {
            filters: [
                ["Item", "item_group", "not in", excluded_groups],
                ["Item", "disabled", "=", 0]
            ]
        };
    });
};

frappe.ui.form.on('Quotation', {
    refresh: function (frm) {
        // Apply filter initially
        if (frm.doc.items) {
            frm.items.forEach(function (item) {
                filter_leather_items(frm, item.doctype, item.name);
            });
        }
    },
    validate: function (frm) {
        // Optional validation
    }
});

frappe.ui.form.on('Quotation Item', {
    form_render: function (frm, cdt, cdn) {
        filter_leather_items(frm, cdt, cdn);
    },
    item_code: function (frm, cdt, cdn) {
        filter_leather_items(frm, cdt, cdn);
    }
});

// Same for Sales Order
frappe.ui.form.on('Sales Order', {
    refresh: function (frm) {
        if (frm.doc.items) {
            frm.items.forEach(function (item) {
                filter_leather_items(frm, item.doctype, item.name);
            });
        }
    }
});

frappe.ui.form.on('Sales Order Item', {
    form_render: function (frm, cdt, cdn) {
        filter_leather_items(frm, cdt, cdn);
    },
    item_code: function (frm, cdt, cdn) {
        filter_leather_items(frm, cdt, cdn);
    }
});
