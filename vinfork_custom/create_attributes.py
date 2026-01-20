
import frappe

def execute():
    print("🚀 Setting up Master Data for Finished Goods...")

    # 1. Create Item Groups
    item_groups = [
        {"item_group_name": "Finished Goods", "parent_item_group": "All Item Groups", "is_group": 1},
        {"item_group_name": "Sofas", "parent_item_group": "Finished Goods", "is_group": 1},
        {"item_group_name": "Beds", "parent_item_group": "Finished Goods", "is_group": 1},
        {"item_group_name": "Furniture", "parent_item_group": "Finished Goods", "is_group": 1},
        # Sub-groups
        {"item_group_name": "Static Sofas", "parent_item_group": "Sofas", "is_group": 0},
        {"item_group_name": "Motion Sofas", "parent_item_group": "Sofas", "is_group": 0},
        {"item_group_name": "Recliner Sofas", "parent_item_group": "Sofas", "is_group": 0},
        {"item_group_name": "Chester Sofas", "parent_item_group": "Sofas", "is_group": 0},
        {"item_group_name": "Chairs", "parent_item_group": "Furniture", "is_group": 0},
        {"item_group_name": "Tables", "parent_item_group": "Furniture", "is_group": 0},
    ]

    for ig in item_groups:
        if not frappe.db.exists("Item Group", ig["item_group_name"]):
            doc = frappe.new_doc("Item Group")
            doc.update(ig)
            doc.insert()
            print(f"✅ Created Item Group: {ig['item_group_name']}")
        else:
            print(f"ℹ️  Item Group exists: {ig['item_group_name']}")

    # 2. Create Item Attributes
    attributes = {
        "Sofa Config": ["1 Seater", "2 Seater", "3 Seater"],
        "Mechanism": ["Manual", "Single Flip", "Double Flip", "Twin Motor"],
        # Backrest & Headrest: User wants "Fixed" and "Adjustable" as options
        "Backrest Function": ["Fixed", "Adjustable"],
        "Headrest Function": ["Fixed", "Adjustable"],
        "Bed Size": ["King", "Queen"],
        "Storage Type": ["Without Storage", "Manual Storage", "Hydraulic Storage", "Remote Storage"]
    }

    for attr_name, values in attributes.items():
        if not frappe.db.exists("Item Attribute", attr_name):
            doc = frappe.new_doc("Item Attribute")
            doc.attribute_name = attr_name
            doc.item_attribute_values = []
            for v in values:
                # Create an abbreviation (required field)
                # Take first 4 chars or uppercase
                abbr = v[:4].upper()
                if abbr in [x.abbr for x in doc.item_attribute_values]: # Avoid duplicate abbr in same list
                    abbr = v[:5].upper()
                
                doc.append("item_attribute_values", {
                    "attribute_value": v,
                    "abbr": abbr
                })
            doc.insert()
            print(f"✅ Created Attribute: {attr_name}")
        else:
            # Check if values exist, if not add them?
            # For simplicity, assuming existing attributes are fine or manual update.
            # But let's verify values if possible.
            print(f"ℹ️  Attribute exists: {attr_name}")

    frappe.db.commit()
    print("✨ Master Data Setup Complete!")
