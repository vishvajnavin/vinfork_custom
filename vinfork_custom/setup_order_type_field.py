import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
    """
    Adds 'Order Type' field to Sales Order Item.
    Run via: bench execute vinfork_custom.setup_order_type_field.execute
    """
    
    field_def = {
        "fieldname": "order_type",
        "label": "Order Type",
        "fieldtype": "Select",
        "options": "Standard\nNew Product Development\nCustomization",
        "in_list_view": 1,
        "insert_after": "item_name", # Insert after item name for better visibility
        "reqd": 0,
        "default": "Standard"
    }
    
    doctype = "Sales Order Item"
    
    if not frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": "order_type"}):
        create_custom_field(doctype, field_def)
        print(f"✅ Created Custom Field 'order_type' in {doctype}")
    else:
        print(f"⚠️ Custom Field 'order_type' already exists in {doctype}")

    frappe.db.commit()
