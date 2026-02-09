# Server Script: Create Custom Fields for BOM
# Copy this entire script and paste it in ERPNext as a Server Script
# Script Type: API
# Script Name: create_bom_custom_fields

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    """
    Create custom fields in BOM DocType to store order type and sales order reference
    Run this once via bench console or as API endpoint
    """
    
    custom_fields = {
        "BOM": [
            {
                "fieldname": "custom_order_type",
                "label": "Order Type",
                "fieldtype": "Select",
                "options": "Standard\nCustomization\nNPD",
                "insert_after": "company",
                "read_only": 1,
                "description": "Auto-populated from Sales Order"
            },
            {
                "fieldname": "custom_linked_sales_order",
                "label": "Linked Sales Order",
                "fieldtype": "Link",
                "options": "Sales Order",
                "insert_after": "custom_order_type",
                "read_only": 1,
                "description": "Original Sales Order that created this BOM"
            }
        ]
    }
    
    create_custom_fields(custom_fields, update=True)
    frappe.db.commit()
    
    print("✅ Custom fields created successfully in BOM DocType")
    return "Custom fields created"

# To run this script:
# Method 1: Via bench console
# $ bench --site your-site console
# >>> from vinfork_custom.create_bom_custom_fields import execute
# >>> execute()

# Method 2: Make it whitelisted and call via API
@frappe.whitelist()
def create_fields():
    return execute()
