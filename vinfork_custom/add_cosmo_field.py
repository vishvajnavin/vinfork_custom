import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    # Define the custom field
    custom_fields = {
        "Purchase Order Item": [
            {
                "fieldname": "custom_customer_ref",
                "label": "Customer Ref (Cosmo Only)",
                "fieldtype": "Data",
                "insert_after": "item_name",
                "print_hide": 1,
                "no_copy": 1
            }
        ]
    }
    
    create_custom_fields(custom_fields)
    print("✅ Custom Field 'Customer Ref' added to Purchase Order Item.")

if __name__ == "__main__":
    execute()
