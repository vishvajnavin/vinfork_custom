import frappe

@frappe.whitelist()
def update_bom_from_actuals(work_order_name):
    """
    Reads the 'Manufacture' Stock Entry for a given Work Order.
    Calculates the per-unit usage of materials.
    Updates the linked BOM with these real materials.
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

    # 2. Find the "Manufacture" Stock Entry (The one linking to Finish)
    # We look for stock entries linked to this WO with purpose 'Manufacture'
    stock_entries = frappe.get_all("Stock Entry", 
                                   filters={"work_order": work_order_name, "purpose": "Manufacture", "docstatus": 1},
                                   fields=["name"])
    
    if not stock_entries:
        frappe.throw("No 'Manufacture' Stock Entry found. Did you forget to consume materials?")

    # We assume the last one is the valid one if multiple exist (rare case)
    se_name = stock_entries[-1].name 
    se = frappe.get_doc("Stock Entry", se_name)

    # 3. Collect Actual Materials Used
    # Filter: Only Raw Materials (Source Warehouse having something)
    actual_items = []
    
    # Total Quantity Produced in this Run (to calculate per-unit)
    # Usually Work Order Qty, or the finished goods qty in the stock entry
    qty_produced = 0
    for item in se.items:
        if item.is_finished_item:
            qty_produced += item.qty
        
    if qty_produced == 0:
        qty_produced = wo.qty # Fallback to WO Qty if SE is weird

    for item in se.items:
        # We want items that were CONSUMED (Source is set, Target is usually empty or WIP is Source)
        # In Manufacture Entry: Source = WIP, Target = Empty (Consumed) OR Source = Stores...
        # Standard Manufacture: Source = WIP.
        if not item.is_finished_item and not item.is_scrap_item:
            # Logic: If we moved it OUT of WIP, it's a raw material
            actual_items.append({
                "item_code": item.item_code,
                "qty_consumed": item.qty,
                "rate": item.basic_rate
            })

    if not actual_items:
        frappe.throw("No raw materials found in the Stock Entry.")

    # 4. Update the BOM
    # Logic: Cancel -> Amend -> Edit -> Save -> Submit
    
    old_bom = frappe.get_doc("BOM", bom_name)
    
    # Logic Change: Do NOT cancel the old BOM (it's linked to Job Card).
    # Instead, we create a NEW version and make it the default.
    
    # 1. Create New Version (Copy)
    new_bom = frappe.copy_doc(old_bom)
    new_bom.docstatus = 0
    new_bom.amended_from = None # Not technically an amendment of a cancelled doc, just a new version
    new_bom.is_default = 1
    new_bom.is_active = 1
    
    # 2. CLEAR old dummy items
    new_bom.items = []
    
    # 3. INSERT new real items
    for row in actual_items:
        # Calculate Per Unit Qty
        per_unit_qty = row["qty_consumed"] / qty_produced
        
        new_row = new_bom.append("items", {})
        new_row.item_code = row["item_code"]
        new_row.qty = per_unit_qty
        new_row.rate = row["rate"]
        new_row.stock_qty = per_unit_qty 
    
    new_bom.save(ignore_permissions=True)
    new_bom.submit()
    
    # 4. Handle Old BOM (Turn off default)
    # We use db_set to avoid full validation/save loops that might trigger "Active" checks
    if old_bom.is_default:
        frappe.db.set_value("BOM", old_bom.name, "is_default", 0)
        
    return new_bom.name
