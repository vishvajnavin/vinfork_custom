import frappe

def create_bom_on_submit(doc, method):
    """
    Called when a Sales Order is submitted.
    Checks each item; if it needs a BOM and doesn't have one, creates a dummy BOM
    with standard Operations (but NO materials) so Production Plan works.
    """
    # 1. List of Operations to add to every Auto-BOM
    # (Update these names if your actual Operation names are different)
    standard_operations = [
        # {"operation": "Frame Making", "workstation": "Team Guddu", "time_in_mins": 60}, 
        # Example - we will fetch just the operation names if user didn't specify details
    ]
    
    # Fetch ALL active Operations dynamically from the system
    ops_list = frappe.get_all("Operation", fields=["name"])
    if not ops_list:
        frappe.log_error("Auto-BOM: No Operations found. Creating BOM without operations.", "Auto BOM Warning")
        target_ops = []
    else:
        target_ops = [op.name for op in ops_list]

    for item in doc.items:
        # Check if item is a stock item (manufacturing candidate)
        is_stock_item = frappe.db.get_value("Item", item.item_code, "is_stock_item")
        if not is_stock_item:
            continue

        # Check if BOM already exists
        if frappe.db.exists("BOM", {"item": item.item_code, "is_active": 1}):
            continue # Skip, already has one

        # CREATE NEW DUMMY BOM
        try:
            bom = frappe.new_doc("BOM")
            bom.item = item.item_code
            bom.quantity = 1
            bom.is_default = 1
            bom.is_active = 1
            bom.currency = doc.currency or "INR"
            
            # Add Operations
            for op_name in target_ops:
                # specific check to ensure Op exists to prevent crash
                if frappe.db.exists("Operation", op_name):
                    row = bom.append("operations", {})
                    row.operation = op_name
                    # Default time (can be updated by Prod Manager later)
                    row.time_in_mins = 60 
            
            # Note: We purposely DO NOT add any 'items' (Raw Materials)

            bom.save()
            bom.submit()
            frappe.msgprint(f"✅ Auto-created Dummy BOM: {bom.name} for {item.item_code}")

        except Exception as e:
            frappe.log_error(f"Failed to create Auto-BOM for {item.item_code}: {str(e)}", "Auto BOM Error")
