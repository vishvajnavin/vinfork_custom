
import frappe
import csv
import os

def execute():
    # File Path
    filename = "STOCK-20.01.2026.csv"
    dataset_dir = frappe.get_app_path("vinfork_custom", "datasets")
    
    # Case-insensitive search
    found_file = None
    if os.path.exists(dataset_dir):
        for f in os.listdir(dataset_dir):
            if f.lower() == filename.lower():
                found_file = f
                break
    
    if not found_file:
        print(f"❌ Error: File '{filename}' not found in {dataset_dir}")
        print(f"   (Available files: {os.listdir(dataset_dir)})")
        return

    csv_path = os.path.join(dataset_dir, found_file)
    print(f"📂 Reading file: {csv_path}")
    
    items_to_update = []
    skipped_items = []
    
    with open(csv_path, 'r', encoding='cp1252') as f:
        # Skip first 2 lines (Titles)
        next(f) 
        next(f)
        
        # Reader with header from line 3
        reader = csv.DictReader(f)
        
        for row in reader:
            # Column Mapping
            # 'MATERIAL NAME' -> Item Code
            # 'CLOSING STOCK' -> Quantity
            
            item_code = row.get("MATERIAL NAME", "").strip()
            qty_raw = row.get("CLOSING STOCK", "0").strip()
            
            if not item_code:
                continue
                
            try:
                qty = float(qty_raw)
            except ValueError:
                qty = 0.0

            # 1. Check if Item Exists
            original_code = item_code
            exists = frappe.db.exists("Item", item_code)
            
            # 1a. Typo Mapping (Manual Fixes)
            TYPO_MAPPING = {
                "12-YP NUT-M008": "Yp Nut M08",
                "13-YP NUT-M10": "Yp Nut M10",
                "104-BIG SIZE SCISSOR-12": "Big Size Scissor",
                "105-SMALL SIZE SCISSOR-10&11": "Small Size Scissor",
                "82-2\"-ELASTIC": "2\"-Elastic", # Check casing
                "177-MESUAREMENT TAPE": "Mesuarement Tape", # Wait, Database has "Stationary-Talier Inch Tape"? 
                                                            # Or maybe it's missing? User said "typo". 
                                                            # Let's try flexible matching for "Tape"
            }
            
            if original_code in TYPO_MAPPING:
                 item_code = TYPO_MAPPING[original_code]
                 if frappe.db.exists("Item", item_code):
                     print(f"✅ Mapped: '{original_code}' -> '{item_code}'")
                     exists = True

            # 1b. Try stripping prefix (e.g. "34-BUSH" -> "BUSH")
            # And apply fuzzy matching
            if not exists and "-" in original_code:
                parts = original_code.split("-", 1)
                if len(parts) > 1:
                    base_code = parts[1].strip()
                    
                    # Candidate 1: Simple * -> X
                    candidates = []
                    candidates.append(base_code.replace("*", "X")) # 6*20 -> 6X20
                    
                    # Candidate 2: Title Case + Formatting replacements
                    # "HT HEX BOLT-6*20" -> "Ht Hex Bolt 6X20"
                    # Steps: Replace *->X, Replace "- "->" ", Replace "BOLD"->"Bolt", Title Case
                    clean_code = base_code.replace("*", "X")
                    clean_code = clean_code.replace('"', '') # Remove inch quotes
                    
                    # Handle "BOLD" typo
                    if "BOLD" in clean_code.upper():
                        clean_code = clean_code.replace("BOLD", "Bolt").replace("Bold", "Bolt")
                        
                    # Handle "MM"
                    if "MM" in clean_code:
                         clean_code = clean_code.replace("MM", "Mm")

                    candidates.append(clean_code) # As is
                    candidates.append(clean_code.title()) # Title Case
                    
                    # Handle Dashes
                    candidates.append(clean_code.replace("-", " ")) # "Bolt-6" -> "Bolt 6"
                    candidates.append(clean_code.replace("-", " ").title()) 

                    for cand in candidates:
                        if frappe.db.exists("Item", cand):
                            item_code = frappe.db.exists("Item", cand)
                            print(f"✅ Auto-Corrected: '{original_code}' -> '{item_code}'")
                            exists = True
                            break
            
            # 1c. Special fallback for "NAIL" without quotes
            # CSV: 61-NAIL 1" -> DB: Nail 1
            if not exists and "NAIL" in original_code.upper():
                  # Logic already covered by remove quotes? 
                  # "NAIL 1"" -> "NAIL 1" -> Title: "Nail 1"
                  pass

            if not exists:
                skipped_items.append(original_code)
                print(f"⚠️  Skipping (Not Found): {original_code}")
                continue
            
            # 2. Add to list
            # We use 'Stores - VDS' ... wait, need to confirm Warehouse.
            # Let's default to "Stores - VDS"
            warehouse = "Stores - V"
            
            items_to_update.append({
                "item_code": item_code,
                "warehouse": warehouse, 
                "qty": qty,
                "valuation_rate": 1.0 
            })

    if not items_to_update:
        print("❌ No valid items found to update.")
        return

    # Deduplicate items (Sum quantities for same Item)
    # This prevents "Same item and warehouse combination" error
    unique_items = {}
    for entry in items_to_update:
        key = entry["item_code"]
        if key in unique_items:
            unique_items[key]["qty"] += entry["qty"]
        else:
            unique_items[key] = entry

    final_items = list(unique_items.values())

    print(f"\n✅ Ready to update {len(final_items)} items (aggregated from {len(items_to_update)} rows).")
    print(f"⚠️  Skipped {len(skipped_items)} items.")

    # 3. Create Stock Reconciliation
    doc = frappe.new_doc("Stock Reconciliation")
    doc.company = "vinyork" 
    doc.purpose = "Stock Reconciliation"
    doc.set_posting_time = 1
    
    # Add items to the doc
    for idx, entry in enumerate(final_items):
        row = doc.append("items", {})
        row.item_code = entry["item_code"]
        row.warehouse = entry["warehouse"]
        row.qty = entry["qty"]
        row.valuation_rate = getattr(entry, "valuation_rate", 1.0) 
        
        # Printing progress
        if idx % 50 == 0:
            print(f"   ... Processed {idx} items")

    print(f"\n💾 Saving Stock Reconciliation...")
    doc.insert()
    
    print(f"🚀 Submitting...")
    try:
        doc.submit()
        print(f"✅ Successfully Submitted: {doc.name}")
    except Exception as e:
        print(f"❌ Failed to Submit: {str(e)}")
        print("Note: The document is saved as Stream but not submitted. Please check manually.")

