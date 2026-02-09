import frappe

@frappe.whitelist()
def update_bom_from_actuals(work_order_name):
    """
    Reads the 'Manufacture' Stock Entry for a given Work Order.
    Calculates the per-unit usage of materials.
    Based on order type:
    - Standard: Updates existing BOM
    - Customization/NPD: Creates new BOM variant
    """
    if not frappe.has_permission("BOM", "write"):
        frappe.throw("You do not have permission to edit BOMs.")

    # 1. Get Work Order Details
    wo = frappe.get_doc("Work Order", work_order_name)
    if wo.status not in ["Completed", "Closed"]:
        frappe.throw("Work Order must be Completed before updating BOM.")

    bom_name = wo.bom_no
    if not bom_name:
        frappe.throw("No BOM linked to this Work Order.")

    # 2. Get Order Type from linked Sales Order
    order_type = get_order_type_from_work_order(wo)
    
    # 3. Find the "Manufacture" Stock Entry
    stock_entries = frappe.get_all("Stock Entry", 
                                   filters={"work_order": work_order_name, "purpose": "Manufacture", "docstatus": 1},
                                   fields=["name"])
    
    if not stock_entries:
        frappe.throw("No 'Manufacture' Stock Entry found. Did you forget to consume materials?")

    se_name = stock_entries[-1].name 
    se = frappe.get_doc("Stock Entry", se_name)

    # 4. Collect Actual Materials Used
    actual_items = []
    qty_produced = 0
    
    for item in se.items:
        if item.is_finished_item:
            qty_produced += item.qty
        
    if qty_produced == 0:
        qty_produced = wo.qty

    for item in se.items:
        if not item.is_finished_item and not item.is_scrap_item:
            actual_items.append({
                "item_code": item.item_code,
                "qty_consumed": item.qty,
                "rate": item.basic_rate
            })

    if not actual_items:
        frappe.throw("No raw materials found in the Stock Entry.")

    # 5. Update BOM based on Order Type
    old_bom = frappe.get_doc("BOM", bom_name)
    
    # Normalize order type for case-insensitive comparison
    order_type_lower = order_type.lower() if order_type else "standard"
    
    if order_type_lower == "standard":
        # Update existing BOM (standard products improve over time)
        new_bom_name = update_standard_bom(old_bom, actual_items, qty_produced)
        frappe.msgprint(f"✅ Updated Standard BOM: {new_bom_name}")
        
    elif order_type_lower in ["customization", "customisation", "npd", "new product"]:
        # Create NEW BOM variant (handle multiple naming variations)
        new_bom_name = create_bom_variant(old_bom, actual_items, qty_produced, order_type, wo)
        frappe.msgprint(f"✅ Created New {order_type} BOM: {new_bom_name}")
        
    else:
        # Fallback to standard update
        new_bom_name = update_standard_bom(old_bom, actual_items, qty_produced)
        frappe.msgprint(f"✅ Updated BOM: {new_bom_name}")
        
    return new_bom_name


def get_order_type_from_work_order(wo):
    """Get order type from linked Sales Order"""
    try:
        if wo.sales_order:
            # Get Sales Order
            so = frappe.get_doc("Sales Order", wo.sales_order)
            
            # Find matching item in SO
            for item in so.items:
                if item.item_code == wo.production_item:
                    return item.get("custom_order_type") or "Standard"
        
        # Check BOM custom field if exists
        if wo.bom_no:
            bom = frappe.get_doc("BOM", wo.bom_no)
            if hasattr(bom, "custom_order_type") and bom.custom_order_type:
                return bom.custom_order_type
                
    except Exception as e:
        frappe.log_error(f"Error getting order type: {str(e)}", "BOM Update Tool")
    
    return "Standard"  # Default fallback


def update_standard_bom(old_bom, actual_items, qty_produced):
    """Update existing BOM for Standard products"""
    # Create new version
    new_bom = frappe.copy_doc(old_bom)
    new_bom.docstatus = 0
    new_bom.amended_from = None
    new_bom.is_default = 1
    new_bom.is_active = 1
    
    # Clear old items
    new_bom.items = []
    
    # Insert real items
    for row in actual_items:
        per_unit_qty = row["qty_consumed"] / qty_produced
        
        new_row = new_bom.append("items", {})
        new_row.item_code = row["item_code"]
        new_row.qty = per_unit_qty
        new_row.rate = row["rate"]
        new_row.stock_qty = per_unit_qty 
    
    new_bom.save(ignore_permissions=True)
    new_bom.submit()
    
    # Turn off old BOM default
    if old_bom.is_default:
        frappe.db.set_value("BOM", old_bom.name, "is_default", 0)
        
    return new_bom.name


def create_bom_variant(old_bom, actual_items, qty_produced, order_type, wo):
    """Create NEW BOM for Customization/NPD"""
    # Create new BOM
    new_bom = frappe.copy_doc(old_bom)
    new_bom.docstatus = 0
    new_bom.amended_from = None
    
    # Naming strategy
    if order_type == "Customization":
        # NOT default (custom BOMs don't replace standard)
        new_bom.is_default = 0
        new_bom.is_active = 1
        
    elif order_type == "NPD":
        # This becomes the NEW standard for this item
        new_bom.is_default = 1
        new_bom.is_active = 1
    
    # Tag with metadata
    if frappe.db.has_column("BOM", "custom_order_type"):
        new_bom.custom_order_type = order_type
    if frappe.db.has_column("BOM", "custom_linked_sales_order"):
        new_bom.custom_linked_sales_order = wo.sales_order
    
    # Clear old items
    new_bom.items = []
    
    # Insert real items
    for row in actual_items:
        per_unit_qty = row["qty_consumed"] / qty_produced
        
        new_row = new_bom.append("items", {})
        new_row.item_code = row["item_code"]
        new_row.qty = per_unit_qty
        new_row.rate = row["rate"]
        new_row.stock_qty = per_unit_qty 
    
    new_bom.save(ignore_permissions=True)
    new_bom.submit()
    
    # For Customization: Keep old BOM as default
    # For NPD: Turn off old BOM since this is the new standard
    if order_type == "NPD" and old_bom.is_default:
        frappe.db.set_value("BOM", old_bom.name, "is_default", 0)
        
    return new_bom.name


@frappe.whitelist()
def start_work_order_manually(work_order_name):
    """
    Manually start a Work Order by updating its status to 'In Process'.
    This bypasses the standard 'Start' button logic which forces stock entry creation.
    """
    # 1. Check permissions
    if not frappe.has_permission("Work Order", "write"):
        frappe.throw("You do not have permission to edit Work Orders.")
        
    # 2. Validate current status
    status = frappe.db.get_value("Work Order", work_order_name, "status")
    if status != "Not Started":
        frappe.throw(f"Work Order is already {status}. Can only start if 'Not Started'.")
        
    # 3. DIRECT UPDATE (Bypass validations that block status change after submit)
    # We use db_set to avoid triggering the 'validate' method which checks for stock entries
    frappe.db.set_value("Work Order", work_order_name, "status", "In Process", update_modified=False)
    
    # 4. Add a comment to the timeline so there's a record
    frappe.get_doc("Work Order", work_order_name).add_comment(
        "Info", 
        "Work Order started manually (bypassing stock entry) via custom script."
    )
    
    return "Success"
