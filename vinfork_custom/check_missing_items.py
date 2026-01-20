
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
        print(f"❌ Error: File '{filename}' not found.")
        return

    csv_path = os.path.join(dataset_dir, found_file)
    skipped_items = []
    
    with open(csv_path, 'r', encoding='cp1252') as f:
        next(f) 
        next(f)
        reader = csv.DictReader(f)
        
        for row in reader:
            original_code = row.get("MATERIAL NAME", "").strip()
            if not original_code:
                continue

            item_code = original_code
            exists = frappe.db.exists("Item", item_code)
            
            # Logic: Try stripping prefix
            if not exists:
                 # 1a. Typo Mapping
                TYPO_MAPPING = {
                    "12-YP NUT-M008": "Yp Nut M08",
                    "13-YP NUT-M10": "Yp Nut M10",
                    "104-BIG SIZE SCISSOR-12": "Big Size Scissor",
                    "105-SMALL SIZE SCISSOR-10&11": "Small Size Scissor",
                    "82-2\"-ELASTIC": "2\"-Elastic",
                    "177-MESUAREMENT TAPE": "Mesuarement Tape", 
                }
                if item_code in TYPO_MAPPING:
                     item_code = TYPO_MAPPING[item_code]
                     if frappe.db.exists("Item", item_code):
                         exists = True

            # 1b. Try stripping prefix AND Fuzzy Matching
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
                            exists = True
                            break

            if not exists:
                skipped_items.append(original_code)

    # Output Report to Brain
    report_path = "/Users/vishvajnavin/.gemini/antigravity/brain/7b1c389f-4669-457b-b06e-3e2de1288759/skipped_items_report.md"
    
    with open(report_path, "w") as f:
        f.write("# ⚠️ Skipped Items Report\n\n")
        f.write(f"**Total Skipped:** {len(skipped_items)}\n\n")
        f.write("| CSV Row Item Name |\n")
        f.write("| --- |\n")
        for item in skipped_items:
            f.write(f"| `{item}` |\n")

    print(f"✅ Report generated at {report_path}")
