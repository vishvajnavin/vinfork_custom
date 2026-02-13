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
    # Fetch ALL active Operations dynamically from the system, capturing default workstation
    # We use ignore_permissions=True to ensure background script can read them
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
            # Get order type from Sales Order Item
            order_type = item.get("custom_order_type") or "Standard"
            
            bom = frappe.new_doc("BOM")
            bom.item = item.item_code
            bom.quantity = 1
            bom.is_default = 1
            bom.is_active = 1
            bom.currency = doc.currency or "INR"
            bom.company = doc.company 
            
            # Store metadata in BOM for later reference
            # Create custom fields if needed: custom_order_type, custom_linked_sales_order
            if frappe.db.has_column("BOM", "custom_order_type"):
                bom.custom_order_type = order_type
            if frappe.db.has_column("BOM", "custom_linked_sales_order"):
                bom.custom_linked_sales_order = doc.name
            
            bom.with_operations = 1 # Force the checkbox to be checked
            
            # Add Operations
            for op in ops_list:
                row = bom.append("operations", {})
                row.operation = op.name
                row.workstation = op.workstation # CRITICAL: Explicitly set the workstation
                row.time_in_mins = 60 
            
            # Add Dummy Raw Material ("Test 1")
            dummy_item = "Test 1"
            if not frappe.db.exists("Item", dummy_item):
                # Auto-create the dummy item if it doesn't exist
                di = frappe.new_doc("Item")
                di.item_code = dummy_item
                di.item_group = "Raw Material"
                di.stock_uom = "Nos"
                di.is_stock_item = 1
                di.valuation_rate = 0
                di.description = "Placeholder item for Auto-BOM"
                di.save(ignore_permissions=True)
                frappe.msgprint(f"⚠️ Created missing dummy item: {dummy_item}")

            if frappe.db.exists("Item", dummy_item):
                rm_row = bom.append("items", {})
                rm_row.item_code = dummy_item
                rm_row.qty = 1
                rm_row.rate = 0 # Assume 0 cost for dummy
            else:
                 frappe.throw(f"Auto-BOM Failed: Item '{dummy_item}' is missing and could not be created.")

            bom.save(ignore_permissions=True)
            bom.submit()
