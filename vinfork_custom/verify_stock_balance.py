
import frappe
import csv
import os

def execute():
    # File Path
    filename = "STOCK-20.01.2026.csv"
    dataset_dir = frappe.get_app_path("vinfork_custom", "datasets")
    
    # Case-insensitive search (reuse logic)
    found_file = None
    if os.path.exists(dataset_dir):
        for f in os.listdir(dataset_dir):
            if f.lower() == filename.lower():
                found_file = f
                break
    
    if not found_file:
        print(f"❌ Error: File '{filename}' not found.")
        return

    csv_path = os.path.join(dataset_dir, found_file)
    print(f"📂 Verifying against: {csv_path}")

    # Results
    matches = []
    mismatches = []
    not_found = []
    
    # Define Warehouse (must match import)
    warehouse = "Stores - V"

    # 1. Aggregate CSV Quantities first
    csv_totals = {} # resolved_item_code -> total_qty
    csv_mapping = {} # resolved_item_code -> original_name (for reporting)

    with open(csv_path, 'r', encoding='cp1252') as f:
        next(f) 
        next(f) 
        reader = csv.DictReader(f)
        
        for row in reader:
            original_code = row.get("MATERIAL NAME", "").strip()
            qty_csv_raw = row.get("CLOSING STOCK", "0").strip()
            
            if not original_code:
                continue

            try:
                qty_csv = float(qty_csv_raw)
            except ValueError:
                qty_csv = 0.0

            # --- Name Resolution Logic ---
            item_code = original_code
            exists = frappe.db.exists("Item", item_code)
            
            # 1a. Typo Mapping
            TYPO_MAPPING = {
                "12-YP NUT-M008": "Yp Nut M08",
                "13-YP NUT-M10": "Yp Nut M10",
                "104-BIG SIZE SCISSOR-12": "Big Size Scissor",
                "105-SMALL SIZE SCISSOR-10&11": "Small Size Scissor",
                "82-2\"-ELASTIC": "2\"-Elastic",
                "85-2\"-ELASTIC": "2-Elastic",
                "177-MESUAREMENT TAPE": "Mesuarement Tape", 
            }
            if item_code in TYPO_MAPPING:
                 item_code = TYPO_MAPPING[item_code]
                 if frappe.db.exists("Item", item_code):
                     exists = True

            # 1b. Fuzzy / Prefix
            if not exists and "-" in original_code:
                parts = original_code.split("-", 1)
                if len(parts) > 1:
                    base_code = parts[1].strip()
                    
                    candidates = []
                    candidates.append(base_code.replace("*", "X")) 
                    
                    clean_code = base_code.replace("*", "X").replace('"', '')
                    if "BOLD" in clean_code.upper():
                        clean_code = clean_code.replace("BOLD", "Bolt").replace("Bold", "Bolt")
                    if "MM" in clean_code:
                         clean_code = clean_code.replace("MM", "Mm")

                    candidates.append(clean_code)
                    candidates.append(clean_code.title())
                    candidates.append(clean_code.replace("-", " "))
                    candidates.append(clean_code.replace("-", " ").title()) 

                    for cand in candidates:
                        if frappe.db.exists("Item", cand):
                            item_code = frappe.db.exists("Item", cand) 
                            exists = True
                            break
            # -----------------------------------------------------------

            if not exists:
                not_found.append(original_code)
                continue
            
            # Add to Aggregates
            if item_code not in csv_totals:
                csv_totals[item_code] = 0.0
                csv_mapping[item_code] = original_code # Keep last seen name
            
            csv_totals[item_code] += qty_csv

    # 2. Compare Aggregates with DB
    for item_code, total_csv_qty in csv_totals.items():
        # Fetch Actual Stock from ERPNext
        actual_qty = frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty")
        
        if actual_qty is None:
            actual_qty = 0.0
        
        actual_qty = float(actual_qty)

        # Compare
        if abs(actual_qty - total_csv_qty) < 0.01:
            matches.append(f"{item_code}: {actual_qty}")
        else:
            mismatches.append({
                "csv_name": csv_mapping[item_code], # Show original name
                "db_name": item_code,
                "csv_qty": total_csv_qty,
                "db_qty": actual_qty,
                "diff": actual_qty - total_csv_qty
            })

    # Summary
    print(f"\n📊 Verification Check:")
    print(f"✅ Exact Matches: {len(matches)}")
    print(f"❌ Mismatches: {len(mismatches)}")
    print(f"⚠️  Not Found in DB: {len(not_found)}")
    
    if mismatches:
        print("\n📝 Detailed Mismatches (CSV vs DB):")
        print(f"{'Item Name':<40} | {'CSV':<10} | {'DB':<10} | {'Diff'}")
        print("-" * 75)
        for m in mismatches:
            print(f"{m['db_name'][:40]:<40} | {m['csv_qty']:<10} | {m['db_qty']:<10} | {m['diff']}")

    if not_found:
        print(f"\n⚠️  Items Not Resolved (Skipped Import): {len(not_found)}")

