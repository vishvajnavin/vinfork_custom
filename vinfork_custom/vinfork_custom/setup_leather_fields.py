import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
    # Field Definition
    field_def = {
        "fieldname": "leather_colour",
        "label": "Leather Colour",
        "fieldtype": "Link",
        "options": "Item",
        "in_list_view": 1,
        "insert_after": "item_code", 
        "reqd": 0 
    }

    # Doctypes to update
    doctypes = ["Quotation Item", "Sales Order Item"]

    for dt in doctypes:     
        if not frappe.db.exists("Custom Field", {"dt": dt, "fieldname": "leather_colour"}):
            create_custom_field(dt, field_def)
            print(f"✅ Added 'Leather Colour' to {dt}")
        else:
            print(f"ℹ️  'Leather Colour' exists in {dt}")

    frappe.db.commit()
