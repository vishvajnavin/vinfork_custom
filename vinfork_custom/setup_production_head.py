import frappe

def execute():
    role_name = "Production Head"
    
    # 1. Create Role
    if not frappe.db.exists("Role", role_name):
        role = frappe.new_doc("Role")
        role.role_name = role_name
        role.desk_access = 1
        role.save()
        print(f"✅ Role '{role_name}' created.")
    else:
        print(f"ℹ️ Role '{role_name}' already exists.")

    # 2. Define Permissions
    # Structure: "Doctype": ["perm1", "perm2", ...]
    # Full Access defaults: read, write, create, submit, cancel, amend, report
    full_perms = ["read", "write", "create", "submit", "cancel", "amend", "report"]
    read_perms = ["read", "report"]

    configs = {
        # --- FULL CONTROL (Manufacturing & Quality) ---
        "Work Order": full_perms,
        "Production Plan": full_perms,
        "Job Card": full_perms,
        "BOM": full_perms,
        "Quality Inspection": full_perms,
        "Operation": full_perms,
        "Workstation": full_perms,
        "Stock Entry": full_perms, # Required to move materials
        "Timesheet": full_perms,   # Often needed for labor tracking
        
        # --- VIEW ONLY (Sales, Item, Stock) ---
        "Sales Order": read_perms,
        "Item": read_perms,
        "Bin": read_perms,         # For Stock Balance checking
        "Warehouse": read_perms,
        "Stock Ledger Entry": read_perms,
        "Batch": read_perms,
    }

    # 3. Apply Permissions (Using Custom DocPerm to override defaults)
    for dt, perms in configs.items():
        # Check if perm exists
        filters = {"role": role_name, "parent": dt}
        if not frappe.db.exists("Custom DocPerm", filters):
            d = frappe.new_doc("Custom DocPerm")
            d.parent = dt
            d.role = role_name
            for p in perms:
                d.set(p, 1)
            d.save()
            print(f"   + Permissions set for {dt}")
        else:
             # Basic update loop if needed, but assuming fresh or non-conflicting
             pass

    frappe.db.commit()
    print("✨ 'Production Head' Role Configured Successfully!")

if __name__ == "__main__":
    execute()
