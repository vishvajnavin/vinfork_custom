
import frappe

def execute():
    print("🚀 Auto-Generating Product Bundles for Static Sofas...")
    
    # 1. Fetch Static Sofa Templates
    # We only want items that have variants and are in Static Sofas group
    templates = frappe.get_all("Item", 
        filters={"item_group": "Static Sofas", "has_variants": 1}, 
        fields=["name", "item_code"]
    )
    
    print(f"Found {len(templates)} Templates in Static Sofas.")

    for temp in templates:
        print(f"\nProcessing: {temp.name}")
        
        # 2. Disable Maintenance Stock
        try:
            doc = frappe.get_doc("Item", temp.name)
            if doc.is_stock_item == 1:
                doc.is_stock_item = 0
                doc.save()
                print(f"   ✅ Disabled 'Maintain Stock' for Template")
        except Exception as e:
            print(f"   ❌ Failed to disable stock: {e}")
            continue

        # 3. Fetch Variants & Group by Extra Attributes
        variants = frappe.get_all("Item", 
            filters={"variant_of": temp.name},
            fields=["name"] 
        )
        
        # Map: { (('Headrest', 'Fixed'),): {'3 Seater': item_name, '2 Seater': item_name} }
        grouped_variants = {} 
        
        for v in variants:
            # Get attributes for this variant
            # Note: direct SQL or specific call is faster, but loop is okay for <1000 items
            v_attrs = frappe.get_all("Item Variant Attribute", 
                filters={"parent": v.name}, 
                fields=["attribute", "attribute_value"]
            )
            attr_map = {d.attribute: d.attribute_value for d in v_attrs}
            
            config = attr_map.get("Sofa Config")
            if not config:
                # Might be a variant that doesn't track seater? Skip.
                continue
            
            # Key for everything ELSE (Color, Headrest, etc.)
            # Sort to ensure tuple key is stable
            extra_key = tuple(sorted([(k, v) for k, v in attr_map.items() if k != "Sofa Config"]))
            
            if extra_key not in grouped_variants:
                grouped_variants[extra_key] = {}
            
            grouped_variants[extra_key][config] = v.name

        # 4. Create Bundles for each Group
        for key, items_map in grouped_variants.items():
            # key is tuple of extra attributes e.g. (('Headrest', 'Fixed'),)
            
            # Suffix construction
            suffix = ""
            if key:
                vals = [x[1] for x in key]
                # Join simple values "Fixed", "Adjustable" -> "-Fixed"
                suffix = "-" + "-".join(vals)
            
            # Check availability
            has_3 = "3 Seater" in items_map
            has_2 = "2 Seater" in items_map
            has_1 = "1 Seater" in items_map
            
            bundles_to_make = []
            
            # Define Combinations
            if has_3 and has_2 and has_1:
                bundles_to_make.append({"s": "SET-3-2-1", "q": {"3 Seater": 1, "2 Seater": 1, "1 Seater": 1}})
            if has_3 and has_2:
                bundles_to_make.append({"s": "SET-3-2",   "q": {"3 Seater": 1, "2 Seater": 1}})
            if has_3 and has_1:
                bundles_to_make.append({"s": "SET-3-1",   "q": {"3 Seater": 1, "1 Seater": 1}})
            if has_2 and has_1:
                bundles_to_make.append({"s": "SET-2-1",   "q": {"2 Seater": 1, "1 Seater": 1}})

            for b in bundles_to_make:
                # Name: GALAXY-Fixed-SET-3-2-1
                bundle_code = f"{temp.name}{suffix}-{b['s']}"
                
                # A. Create Item (Sales Set)
                if not frappe.db.exists("Item", bundle_code):
                    i_doc = frappe.new_doc("Item")
                    i_doc.item_code = bundle_code
                    i_doc.item_name = bundle_code
                    i_doc.item_group = "Static Sofas"
                    i_doc.is_stock_item = 0 # Bundle parent is a service/set
                    i_doc.insert()
                    print(f"      Created Item: {bundle_code}")
                
                # B. Create Product Bundle
                if not frappe.db.exists("Product Bundle", bundle_code):
                    pb = frappe.new_doc("Product Bundle")
                    pb.new_item_code = bundle_code
                    
                    for seat_conf, qty in b['q'].items():
                        child_code = items_map[seat_conf]
                        pb.append("items", {
                            "item_code": child_code,
                            "qty": qty
                        })
                    pb.insert()
                    print(f"      ✅ Created Bundle: {bundle_code}")
                else:
                    print(f"      ℹ️  Bundle exists: {bundle_code}")

    frappe.db.commit()
    print("✨ Product Bundle Setup Complete!")
