
import frappe
import csv
import os

def execute():
    # File Path
    filename = "model_and_sofa_type.csv"
    dataset_dir = frappe.get_app_path("vinfork_custom", "datasets")
    csv_path = os.path.join(dataset_dir, filename)
    
    if not os.path.exists(csv_path):
        print(f"❌ Error: File '{filename}' not found.")
        return

    print(f"🚀 Creating Finished Goods from: {filename}")

    # Standard Attributes (Created via create_attributes.py)
    # We just explicitly name them here for logic
    SOFA_CONFIG = "Sofa Config"
    MECHANISM = "Mechanism"
    BACKREST = "Backrest Function"
    HEADREST = "Headrest Function"
    BED_SIZE = "Bed Size"
    STORAGE = "Storage Type"

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            model_name = row.get("Model Name", "").strip()
            sofa_type = row.get("Sofa Type", "").strip()
            
            if not model_name: 
                continue

            print(f"Processing: {model_name} ({sofa_type})")
            
            # 1. Determine Identity (Item Group / Has Variants?)
            item_group = "Finished Goods"
            has_variants = False
            attributes = []

            # --- Logic Rule Engine ---
            
            # CASE A: BEDS
            if "Bed" in sofa_type or "BED" in sofa_type.upper() or "King" in sofa_type:
                item_group = "Beds"
                has_variants = True
                attributes.append({"attribute": BED_SIZE})
                attributes.append({"attribute": STORAGE})
            
            # CASE B: FURNITURE (Chairs / Table / CT)
            elif "Chair" in sofa_type or "CT" in sofa_type or "TABLE" in sofa_type or "Bench" in sofa_type:
                item_group = "Furniture" # Or specific "Chairs"/"Tables" if mapped
                if "Chair" in sofa_type: item_group = "Chairs"
                if "CT" in sofa_type or "TABLE" in sofa_type: item_group = "Tables"
                has_variants = False # As per user: "chairs no varients"
            
            # CASE C: SOFAS (Static / Motion / Chester)
            else:
                has_variants = True
                attributes.append({"attribute": SOFA_CONFIG}) # Always 3str/2str/1str for sofas

                # C1. Motion / Recliner
                if "Motion" in sofa_type or "Recliner" in sofa_type:
                    item_group = "Motion Sofas" if "Motion" in sofa_type else "Recliner Sofas"
                    attributes.append({"attribute": MECHANISM}) # Always add Mechanism for Motion
                
                # C2. Static / Chester
                elif "Chester" in sofa_type:
                    item_group = "Chester Sofas"
                else:
                    item_group = "Static Sofas"

                # C3. Check for Adjustable Features in "Sofa Type" string
                if "Headrest Adjustable" in sofa_type:
                    attributes.append({"attribute": HEADREST})
                if "Backrest Adjustable" in sofa_type:
                    attributes.append({"attribute": BACKREST})

            # ---------------------------

            # 2. Create Item (Template or Standard)
            
            # Check if Item exists
            if frappe.db.exists("Item", model_name):
                # Update? Or Skip? User said "make sure u do this all".
                # Let's Skip to avoid error, or just ensure it's a template?
                print(f"   ⚠️  Item {model_name} already exists. Skipping creation.")
                continue

            doc = frappe.new_doc("Item")
            doc.item_code = model_name
            doc.item_name = model_name
            doc.item_group = item_group
            doc.is_stock_item = 1
            doc.stock_uom = "Nos"
            
            if has_variants:
                doc.has_variants = 1
                doc.variant_based_on = "Item Attribute"
                for attr_dict in attributes:
                     doc.append("attributes", attr_dict)
            
            doc.insert()
            print(f"   ✅ Created: {model_name} (Group: {item_group}, Variants: {has_variants})")

            # 3. Auto-Create Variants (If Template)
            if has_variants:
                create_variants_for_template(doc)

    frappe.db.commit()
    print("✨ Finished Goods Creation Complete!")

def create_variants_for_template(template):
    # Logic to create all combinations
    # This is complex because we need to combinatorial.
    # Fortunately, frappe.model.create_new_variant helps, but specific combinations only?
    # User said: "add all 3 sofa config... and for motion add mechanism... all combinations of bed..."
    
    # We need to construct the attribute combinations manually or use a helper
    # For simplicity, we will generate ALL valid combinations of the attributes assigned.
    
    # Python List of Lists for Cartesian Product
    import itertools
    
    attr_names = [d.attribute for d in template.attributes]
    possible_values = []
    
    for attr in attr_names:
        # Get values from DB
        values = frappe.get_all("Item Attribute Value", filters={"parent": attr}, fields=["attribute_value"])
        vals = [v.attribute_value for v in values]
        possible_values.append(vals)
    
    # Generate Cartesian Product
    combinations = list(itertools.product(*possible_values))
    
    print(f"      ... Generating {len(combinations)} Variants...")
    
    count = 0
    for combo in combinations:
        # Check if variant exists
        # Construct Variant Code? Usually ERPNext does this automatically via quick entry or `make_variant`
        # But we want to do it programmatically.
        
        variant = frappe.new_doc("Item")
        variant.is_stock_item = 1
        variant.stock_uom = "Nos"
        variant.item_group = template.item_group
        variant.variant_of = template.name
        variant.has_variants = 0
        variant.attributes = []
        
        # Suffix for Item Code
        suffix_parts = []
        
        for idx, val in enumerate(combo):
            attr_name = attr_names[idx]
            variant.append("attributes", {
                "attribute": attr_name,
                "attribute_value": val
            })
            suffix_parts.append(str(val))
        
        # Suggest Item Code: MODEL-Var1-Var2...
        # ERPNext usually handles this, but let's force a clean naming if possible.
        # Actually, let's just insert(). ERPNext auto-generates code if naming series is set, 
        # or we might need to set it.
        # Default behavior: Item Code is specific.
        # Let's try explicit naming to match plan: "GALAXY-3 Seater"
        
        variant_code = f"{template.name}-" + "-".join(suffix_parts)
        variant.item_code = variant_code
        variant.item_name = variant_code
        
        if frappe.db.exists("Item", variant_code):
            continue

        try:
            variant.insert()
            count += 1
        except Exception as e:
            print(f"      ❌ Failed to create {variant_code}: {e}")

    print(f"      ✅ Created {count} variants.")
