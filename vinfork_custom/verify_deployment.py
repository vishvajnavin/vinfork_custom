import frappe

def check():
    print("---------------------------------------------------")
    print("🔍 Starting Deployment Verification for Vinfork Custom")
    print("---------------------------------------------------")

    # 1. Check Module Import
    try:
        import vinfork_custom.auto_bom
        print("✅ SUCCESS: 'vinfork_custom.auto_bom' module is importable.")
    except ImportError as e:
        print(f"❌ FAILURE: Could not import 'vinfork_custom.auto_bom'. Error: {e}")
        return

    # 2. Check Hook Registration
    try:
        hooks = frappe.get_hooks("doc_events")
        so_hooks = hooks.get("Sales Order", {})
        on_submit = so_hooks.get("on_submit", [])
        
        target_hook = "vinfork_custom.auto_bom.create_bom_on_submit"
        
        # on_submit can be a list or a single string
        if isinstance(on_submit, list):
            found = any(target_hook in str(h) for h in on_submit)
        else:
            found = target_hook in str(on_submit)
            
        if found:
            print(f"✅ SUCCESS: Hook '{target_hook}' is registered for Sales Order > on_submit.")
        else:
            print(f"❌ FAILURE: Hook '{target_hook}' is NOT found in doc_events.")
            print(f"   Current hooks for Sales Order > on_submit: {on_submit}")
            print("   👉 Solution: Run 'bench migrate' to refresh hooks.")
            
    except Exception as e:
        print(f"❌ ERROR checking hooks: {e}")

    print("---------------------------------------------------")
    print("Verification Complete.")
