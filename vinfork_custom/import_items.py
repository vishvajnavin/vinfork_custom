import frappe
import csv
import os

def execute():
    # Path to your CSV
    csv_path = frappe.get_app_path("vinfork_custom", "datasets", "items.csv")

    if not os.path.exists(csv_path):
        print(f"ERROR: File not found at {csv_path}")
        return

    # Create Root Item Group if missing
    if not frappe.db.exists("Item Group", "All Item Groups"):
        root = frappe.new_doc("Item Group")
        root.item_group_name = "All Item Groups"
        root.is_group = 1
        root.parent_item_group = "" 
        root.insert(ignore_permissions=True)
        print("✅ Created missing Root Item Group: All Item Groups")

    # Create Item Group if missing
    if not frappe.db.exists("Item Group", "Raw Material"):
        ig = frappe.new_doc("Item Group")
        ig.item_group_name = "Raw Material"
        ig.parent_item_group = "All Item Groups"
        ig.is_group = 0
        ig.insert(ignore_permissions=True)
        print("✅ Created missing Item Group: Raw Material")


    # UOM Mapping (CSV -> ERPNext)
    uom_map = {
        "Kgs": "Kg",
        "Mtr": "Meter",
        "Pcs": "Nos",
        "Box": "Box",
        "Set": "Set",
        "Roll": "Roll",
        "Nos": "Nos",
        "Ltr": "Litre",
        "Bundal": "Nos"
    }

    success_count = 0
    error_count = 0

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            original_uom = row.get("UOM", "").strip()
            item_name = row.get("Item Name", "").strip()
            
            # Map UOM or default to 'Nos' if unknown
            erpnext_uom = uom_map.get(original_uom, "Nos")
            
            # Skip empty rows
            if not item_name:
                continue

            try:
                # Check if item exists
                if not frappe.db.exists("Item", item_name):
                    doc = frappe.get_doc({
                        "doctype": "Item",
                        "item_code": item_name,
                        "item_name": item_name,
                        "item_group": "Raw Material",
                        "stock_uom": erpnext_uom,
                        "is_stock_item": 1,
                        "valuation_rate": 0, # Default value required
                         "description": "Imported via Script"
                    })
                    doc.insert()
                    print(f"✅ Created: {item_name} (UOM: {erpnext_uom})")
                    success_count += 1
                else:
                    print(f"⚠️  Skipped (Exists): {item_name}")
            
            except Exception as e:
                print(f"❌ Failed: {item_name} | Error: {str(e)}")
                error_count += 1
    
    frappe.db.commit()
    print(f"\n--- Import Summary ---")
    print(f"Success: {success_count}")
    print(f"Errors: {error_count}")
