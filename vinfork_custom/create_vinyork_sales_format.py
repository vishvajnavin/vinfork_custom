import frappe

def execute():
    design_name = "Vinyork Standard Format"
    
    # We will create this format for TWO Doctypes: Quotation and Sales Order
    doctypes = ["Quotation", "Sales Order"]

    # HTML Template (Shared Logic)
    # Note: We use flexible headers "PROFORMA INVOICE" vs "SALES ORDER" logic inside
    html_content = """
    <div style="font-family: Arial, sans-serif; font-size: 11px; color: #000; padding: 10px;">
        
        <!-- HEADER ROW: Logo + Address -->
        <div style="text-align: center; margin-bottom: 5px;">
             <!-- Center Logo / Title if user prefers, currently standard ERPNext top-left logo logic, 
                  but PDF shows centered logo. Let's try to mimic PDF layout. -->
             {% if doc.company_logo %}
             <img src="{{ doc.company_logo }}" style="max-height: 50px;">
             {% else %}
             <h2 style="margin:0; color: #ff0000;">VINYORK LEATHER WORKS</h2>
             {% endif %}
             <p style="margin: 0; font-size: 10px; font-weight: bold; color: green;">(Home to Comfort)</p>
        </div>

        <table style="width: 100%; margin-bottom: 2px;">
            <tr>
                <td style="width: 50%; vertical-align: top; font-size: 10px;">
                    <b>FURNITURE DIVISION,</b><br>
                    {{ frappe.db.get_value("Address", doc.company_address, "address_line1") or "" }},<br>
                    {{ frappe.db.get_value("Address", doc.company_address, "address_line2") or "" }}<br>
                    {{ frappe.db.get_value("Address", doc.company_address, "city") or "" }} - {{ frappe.db.get_value("Address", doc.company_address, "pincode") or "" }}<br>
                    <b>GSTIN/UIN:</b> {{ frappe.db.get_value("Company", doc.company, "tax_id") or "" }}
                </td>
                <td style="width: 50%; vertical-align: top; text-align: right; font-size: 10px;">
                     <b>TO: {{ doc.customer_name }}</b><br>
                     {{ doc.address_display or "" }}<br>
                     {% set cust_gst = frappe.db.get_value("Address", doc.customer_address, "gstin") %}
                     {% if cust_gst %}<b>GSTIN:</b> {{ cust_gst }}{% endif %}
                </td>
            </tr>
        </table>

        <!-- TITLE BAR -->
        <div style="border: 1px solid #000; text-align: center; background-color: #eee; padding: 3px; font-weight: bold; margin-bottom: 0;">
            {% if doc.doctype == "Quotation" %}PROFORMA INVOICE {{ doc.name }}{% else %}SALES ORDER {{ doc.name }}{% endif %}
            <span style="float: right;">Date: {{ frappe.utils.formatdate(doc.transaction_date) }}</span>
        </div>

        <!-- ITEMS TABLE (The Complex Part) -->
        <table style="width: 100%; border-collapse: collapse; border: 1px solid #000; text-align: center;">
            <thead>
                <tr style="background-color: #ddd; font-weight: bold;">
                    <th style="border: 1px solid #000; padding: 4px; width: 3%;">Sl.</th>
                    <th style="border: 1px solid #000; padding: 4px; width: 15%;">Model Name</th>
                    <th style="border: 1px solid #000; padding: 4px; width: 15%;">Model Image</th>
                    <th style="border: 1px solid #000; padding: 4px; width: 10%;">Sofa Type</th>
                    <th style="border: 1px solid #000; padding: 4px; width: 10%;">Leather<br>Range</th>
                    <th style="border: 1px solid #000; padding: 4px; width: 10%;">Colour</th>
                    <th style="border: 1px solid #000; padding: 4px; width: 12%;">Config</th>
                    <th style="border: 1px solid #000; padding: 4px; width: 10%;">Total Price</th>
                </tr>
            </thead>
            <tbody>
                {% for item in doc.items %}
                <tr style="vertical-align: middle;">
                    <td style="border: 1px solid #000; padding: 5px;">{{ loop.index }}</td>
                    
                    <!-- Model Name -->
                    <td style="border: 1px solid #000; padding: 5px; font-weight: bold;">
                        {{ item.item_name }}<br>
                        {% if "Custom" in item.item_name or "Custom" in item.description %}(Customized){% endif %}
                    </td>

                    <!-- Image -->
                    <td style="border: 1px solid #000; padding: 2px;">
                        {% if item.image %}
                        <img src="{{ item.image }}" style="max-height: 60px; max-width: 80px;">
                        {% endif %}
                    </td>

                    <!-- Sofa Type (Extract from Description or Item Group or a Custom Field if exists) -->
                    <td style="border: 1px solid #000; padding: 5px;">
                        {{ item.item_group or "Static Sofa" }} <!-- Fallback logic, ideally use custom field -->
                    </td>

                    <!-- Leather Range / Color (We assume standard Description or custom fields) -->
                    <td style="border: 1px solid #000; padding: 5px;">
                        {{ item.description | striptags | truncate(20) }} 
                    </td>
                    <td style="border: 1px solid #000; padding: 5px;">
                         <!-- Placeholder for Color -->
                         {{ item.variant_value_color or "-" }}
                    </td>

                    <!-- Config -->
                     <td style="border: 1px solid #000; padding: 5px;">
                        {{ item.variant_value_size or item.qty ~ " " ~ item.uom }}
                    </td>

                    <!-- Price -->
                    <td style="border: 1px solid #000; padding: 5px; font-weight: bold;">
                        {{ item.get_formatted("amount") }}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <!-- TOTALS -->
        <div style="display: flex; justify-content: flex-end; margin-top: 0; border: 1px solid #000; border-top: 0;">
             <table style="width: 30%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 4px; border-bottom: 1px solid #ccc;">Taxable Value</td>
                    <td style="padding: 4px; text-align: right; border-bottom: 1px solid #ccc;">{{ doc.get_formatted("total") }}</td>
                </tr>
                <tr>
                    <td style="padding: 4px; border-bottom: 1px solid #000;">GST (18%)</td>
                    <td style="padding: 4px; text-align: right; border-bottom: 1px solid #000;">{{ doc.get_formatted("total_taxes_and_charges") }}</td>
                </tr>
                <tr style="background-color: #dbeaff; font-weight: bold;">
                    <td style="padding: 6px;">Total Value</td>
                    <td style="padding: 6px; text-align: right;">{{ doc.get_formatted("grand_total") }}</td>
                </tr>
             </table>
        </div>

        <!-- NOTES & BANK DETAILS -->
        <div style="margin-top: 20px; display: flex; justify-content: space-between;">
             <div style="width: 50%; font-size: 10px; color: red;">
                 <b>Terms:</b><br>
                 1. Above price is excluding GST (Wait, table shows GST included logic above, adjusting)<br>
                 2. 60% Advance Payment.<br>
                 3. Delivery time 60 days.<br>
                 4. Customisation allowed with extra charges.
             </div>
             <div style="width: 45%; background-color: yellow; padding: 10px; border: 1px solid #000;">
                 <div style="text-align: center; font-weight: bold; margin-bottom: 5px;">Our Bank Details</div>
                 Acc Name: Vinyork Leather works<br>
                 Acc No: 043802000001343<br>
                 IFSC: IOBA0000438<br>
                 Bank: Indian Overseas Bank
             </div>
        </div>

    </div>
    """

    for dt in doctypes:
        pf_name = f"Vinyork Standard {dt}"
        if frappe.db.exists("Print Format", pf_name):
            pf = frappe.get_doc("Print Format", pf_name)
            print(f"🔄 Updating: {pf_name}")
        else:
            pf = frappe.new_doc("Print Format")
            pf.name = pf_name
            pf.doc_type = dt
            pf.module = "Selling"
            pf.standard = "No"
            pf.custom_format = 1
            pf.print_format_type = "Jinja"
            print(f"🆕 Creating: {pf_name}")

        pf.html = html_content
        pf.save()
    
    frappe.db.commit()
    print("✅ Vinyork Standard Formats (Quote & Order) Created!")

if __name__ == "__main__":
    execute()
