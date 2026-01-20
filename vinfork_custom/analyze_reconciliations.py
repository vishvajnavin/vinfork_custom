
import frappe

def execute():
    # The 3 documents we created
    reco_ids = ["MAT-RECO-2026-00004", "MAT-RECO-2026-00005", "MAT-RECO-2026-00006"]
    
    all_items = set()
    usage_map = {} # item_code -> [reco_id1, reco_id2]
    
    print(f"📊 Analyzing Stock Reconciliations: {reco_ids}")
    
    for rid in reco_ids:
        if not frappe.db.exists("Stock Reconciliation", rid):
            print(f"❌ Document {rid} not found.")
            continue
            
        doc = frappe.get_doc("Stock Reconciliation", rid)
        print(f"\n📄 {rid}: {len(doc.items)} items")
        
        for item in doc.items:
            all_items.add(item.item_code)
            
            if item.item_code not in usage_map:
                usage_map[item.item_code] = []
            usage_map[item.item_code].append(rid)

    print(f"\n------------------------------------------------")
    print(f"🔢 Total Distinct Items Affected: {len(all_items)}")
    print(f"------------------------------------------------")
    
    # Check for items that were in earlier rounds but NOT in Round 3 (0006)
    missing_in_latest = []
    latest_reco_items = [i.item_code for i in frappe.get_doc("Stock Reconciliation", "MAT-RECO-2026-00006").items]
    
    for item in all_items:
        if item not in latest_reco_items:
            missing_in_latest.append(item)
            
    if missing_in_latest:
        print(f"⚠️  {len(missing_in_latest)} Items were in earlier runs but NOT in the latest (0006):")
        print(missing_in_latest)
    else:
        print("✅ Round 3 (0006) included ALL items from previous rounds.")

