import frappe
from vinfork_custom.auto_bom import create_bom_on_submit

def run_test():
    frappe.db.rollback() # Start fresh

    # 1. Setup Data
    item_code = "Auto BOM Test Item"
    dummy_rm = "Test 1"
    
    # Create Dummy RM
    if not frappe.db.exists("Item", dummy_rm):
        rm_doc = frappe.new_doc("Item")
        rm_doc.item_code = dummy_rm
        rm_doc.item_group = "Raw Material"
        rm_doc.is_stock_item = 1
        rm_doc.stock_uom = "Nos" # Fix: Mandatory
        rm_doc.save()

    # Create Finished Item
    if not frappe.db.exists("Item", item_code):
        fl_doc = frappe.new_doc("Item")
        fl_doc.item_code = item_code
        fl_doc.item_group = "Products"
        fl_doc.is_stock_item = 1
        fl_doc.stock_uom = "Nos" # Fix: Mandatory
        fl_doc.save()
    
    frappe.db.sql("DELETE FROM `tabBOM` WHERE item=%s", item_code)

    # Create Dummy Operation and Workstation
    op_name = "Test Operation"
    ws_name = "Test Workstation"
    if not frappe.db.exists("Workstation", ws_name):
        ws = frappe.new_doc("Workstation")
        ws.workstation_name = ws_name
        ws.save()
        
    if not frappe.db.exists("Operation", op_name):
        op = frappe.new_doc("Operation")
        op.operation = op_name
        op.name = op_name # Fix: Autoname Prompt
        op.workstation = ws_name 
        op.insert()

    # 2. Create Sales Order
    so = frappe.new_doc("Sales Order")
    so.customer = "Test Customer" 
    if not frappe.db.exists("Customer", "Test Customer"):
        c = frappe.new_doc("Customer")
        c.customer_name = "Test Customer"
        c.save()
        
    so.transaction_date = frappe.utils.nowdate()
    so.delivery_date = frappe.utils.add_days(frappe.utils.nowdate(), 7)
    so.company = "Vinforksofas" 
    so.currency = "INR"
    so.selling_price_list = "Standard Selling"
    # Ensure Price List exists
    if not frappe.db.exists("Price List", "Standard Selling"):
        pl = frappe.new_doc("Price List")
        pl.price_list_name = "Standard Selling"
        pl.selling = 1
        pl.currency = "INR"
        pl.save() 
    warehouse = frappe.db.get_value("Warehouse", {"is_group": 0})
    so.append("items", {
        "item_code": item_code,
        "qty": 1,
        "delivery_date": so.delivery_date,
        "warehouse": warehouse
    })
    so.save()
    
    # 3. Simulate Submit (Trigger Hook Manually)
    # We call the function directly to test logic, mimicking hook
    print("Simulating auto_bom hook...")
    create_bom_on_submit(so, "on_submit")
    
    # 4. Verify
    bom_name = frappe.db.get_value("BOM", {"item": item_code}, "name")
    if bom_name:
        print(f"SUCCESS: BOM created: {bom_name}")
        bom_doc = frappe.get_doc("BOM", bom_name)
        print(f"Operations Count: {len(bom_doc.operations)}")
        for op in bom_doc.operations:
            print(f" - Op: {op.operation}, Workstation: {op.workstation}")
    else:
        print("FAILURE: BOM was not created.")

    frappe.db.rollback() 

