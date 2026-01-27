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
    
    # Fetch ALL active Operations dynamically from the system, capturing default workstation
    # We use ignore_permissions=True to ensure background script can read them
    ops_list = frappe.get_all("Operation", fields=["name", "workstation"], filters={}, ignore_permissions=True)

    if not ops_list:
        frappe.log_error("Auto-BOM: No Operations found. Creating BOM without operations.", "Auto BOM Warning")

    # ... inside BOM creation ...
    for item in doc.items:
        # Check if item is a stock item (manufacturing candidate)
        is_stock_item = frappe.db.get_value("Item", item.item_code, "is_stock_item")
        if not is_stock_item:
            continue

        if not frappe.db.exists("BOM", {"item": item.item_code, "is_active": 1}):
        try:
            bom = frappe.new_doc("BOM")
            bom.item = item.item_code
            bom.quantity = 1
            bom.is_default = 1
            bom.is_active = 1
            bom.currency = doc.currency or "INR"
            
            bom.with_operations = 1 # Force the checkbox to be checked
            
            # Add Operations
            for op in ops_list:
                row = bom.append("operations", {})
                row.operation = op.name
                row.workstation = op.workstation # CRITICAL: Explicitly set the workstation
                row.time_in_mins = 60 
            
            # Add Dummy Raw Material ("Test 1")
            dummy_item = "Test 1"
            if frappe.db.exists("Item", dummy_item):
                rm_row = bom.append("items", {})
                rm_row.item_code = dummy_item
                rm_row.qty = 1
                rm_row.rate = 0 # Assume 0 cost for dummy
            else:
                 frappe.log_error(f"Auto-BOM: Dummy item '{dummy_item}' not found.", "Auto BOM Warning")

            bom.save()
            bom.submit()
            frappe.msgprint(f"✅ Auto-created Dummy BOM: {bom.name} for {item.item_code}")

        except Exception as e:
            frappe.log_error(f"Failed to create Auto-BOM for {item.item_code}: {str(e)}", "Auto BOM Error")
