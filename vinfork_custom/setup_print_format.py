import frappe

def execute():
    """
    Installs the 'Vinfork Zoho Style' Print Format for Sales Order.
    Run via: bench execute vinfork_custom.setup_print_format.execute
    """
    
    # HTML Template (Zoho Style - Professional)
    html_content = """
<style>
    .print-format {
        font-family: "Inter", "Helvetica Neue", Helvetica, Arial, sans-serif;
        color: #1f2937;
        line-height: 1.6;
        font-size: 13px;
        -webkit-font-smoothing: antialiased;
    }
    .header-section {
        margin-bottom: 40px;
        padding-bottom: 20px;
        border-bottom: 2px solid #e5e7eb;
    }
    .company-logo {
        max-height: 100px; /* Increased from 80px */
        max-width: 250px;
        object-fit: contain;
    }
    .doc-title {
        text-align: right;
        font-size: 28px;
        font-weight: 800;
        color: #111827;
        letter-spacing: -0.5px;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    .doc-status {
        text-align: right;
        font-size: 14px;
        color: #6b7280;
        margin-bottom: 2px;
    }
    .address-section {
        display: flex;
        justify-content: space-between;
        margin-bottom: 40px;
        gap: 40px;
    }
    .address-box {
        flex: 1;
    }
    .address-box h4 {
        font-size: 11px;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
        font-weight: 700;
        border-bottom: 1px solid #f3f4f6;
        padding-bottom: 5px;
        display: inline-block;
    }
    .address-content {
        font-size: 14px;
        line-height: 1.5;
    }
    .items-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 30px;
    }
    .items-table th {
        background-color: #f9fafb;
        color: #374151;
        text-align: left;
        padding: 12px 10px;
        font-weight: 600;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border-top: 2px solid #e5e7eb;
        border-bottom: 2px solid #e5e7eb;
    }
    .items-table td {
        border-bottom: 1px solid #f3f4f6;
        padding: 15px 10px;
        vertical-align: middle;
    }
    .items-table tr:last-child td {
        border-bottom: none;
    }
    .item-image {
        width: 80px;
        height: 80px;
        object-fit: contain;
        border-radius: 6px;
        background-color: #fff;
        padding: 2px;
        border: 1px solid #e5e7eb;
    }
    .item-name-cell {
        font-weight: 600;
        font-size: 14px;
        color: #111827;
    }
    .total-section {
        display: flex;
        justify-content: flex-end;
        margin-top: 20px;
        border-top: 2px solid #e5e7eb;
        padding-top: 20px;
    }
    .total-table {
        width: 45%;
        border-collapse: collapse;
    }
    .total-table td {
        padding: 8px 10px;
        text-align: right;
    }
    .total-table .label-col {
        color: #6b7280;
        font-weight: 500;
    }
    .total-table .value-col {
        font-weight: 600;
        color: #374151;
    }
    .grand-total-row td {
        border-top: 1px solid #e5e7eb;
        padding-top: 15px;
        padding-bottom: 5px;
    }
    .grand-total {
        font-size: 18px;
        font-weight: 800;
        color: #111827;
    }
    .terms-section {
        margin-top: 50px;
        border-top: 1px solid #e5e7eb;
        padding-top: 20px;
        font-size: 12px;
        color: #6b7280;
    }
    .terms-section h4 {
        color: #374151;
        font-size: 12px;
        text-transform: uppercase;
        margin-bottom: 8px;
        font-weight: 700;
    }
</style>

<div class="header-section">
    <div class="row">
        <div class="col-xs-6">
            <!-- Logo Section -->
            {% set company_logo = frappe.db.get_value("Company", doc.company, "company_logo") %}
            {% if company_logo %}
                <img src="{{ company_logo }}" class="company-logo" alt="{{ doc.company }}">
            {% else %}
                <h1 style="margin:0; font-size:24px; font-weight:700;">{{ doc.company }}</h1>
            {% endif %}
        </div>
        <div class="col-xs-6 text-right">
            <div class="doc-title">Sales Order</div>
            <div class="doc-status"><span style="color:#9ca3af;">#</span> {{ doc.name }}</div>
            <div class="doc-status">{{ doc.get_formatted("transaction_date") }}</div>
        </div>
    </div>
</div>

<div class="address-section">
    <div class="address-box">
        <h4>Bill To</h4>
        <div class="address-content">
            <div style="font-weight:700; color:#111827;">{{ doc.customer_name }}</div>
            {{ doc.billing_address_display or "" }}
            {% if doc.contact_display %}
                <div style="margin-top:5px; color:#6b7280;">{{ doc.contact_display }}</div>
            {% endif %}
        </div>
    </div>
    {% if doc.shipping_address_name != doc.customer_address %}
    <div class="address-box">
        <h4>Ship To</h4>
        <div class="address-content">
            <div style="font-weight:700; color:#111827;">{{ doc.customer_name }}</div>
            {{ doc.shipping_address_display or "" }}
        </div>
    </div>
    {% endif %}
</div>

<table class="items-table">
    <thead>
        <tr>
            <th width="10%">Image</th>
            <th width="25%">Item</th>
            <th width="12%">Sofa Type</th>
            <th width="12%">Range</th>
            <th width="12%">Leather</th>
            <th width="8%" class="text-right">Qty</th>
            <th width="10%" class="text-right">Rate</th>
            <th width="11%" class="text-right">Amount</th>
        </tr>
    </thead>
    <tbody>
        {% for item in doc.items %}
        <tr>
            <td>
                {% if item.image %}
                    <img src="{{ item.image }}" class="item-image">
                {% else %}
                    <div style="width:50px; height:50px; background:#f3f4f6; border-radius:4px; display:flex; align-items:center; justify-content:center; color:#d1d5db; font-size:10px;">NO IMG</div>
                {% endif %}
            </td>
            <td>
                <div class="item-name-cell">{{ item.item_name }}</div>
            </td>
            <td>
                {{ item.custom_sofa_type or frappe.db.get_value("Item", item.item_code, "custom_sofa_type") or "" }}
            </td>
            <td>
                {{ item.custom_sofa_config_copy or frappe.db.get_value("Item", item.item_code, "custom_sofa_config_copy") or "" }}
            </td>
            <td>
                {{ item.leather_colour or frappe.db.get_value("Item", item.item_code, "leather_colour") or "" }}
            </td>
            <td class="text-right" style="font-weight:500;">{{ item.qty }}</td>
            <td class="text-right">{{ item.get_formatted("rate") }}</td>
            <td class="text-right" style="font-weight:600;">{{ item.get_formatted("amount") }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>

<div class="total-section">
    <table class="total-table">
        <tr>
            <td class="label-col">Subtotal</td>
            <td class="value-col">{{ doc.get_formatted("total") }}</td>
        </tr>
        
        {% for row in doc.taxes %}
        {% if not row.included_in_print_rate %}
        <tr>
            <td class="label-col">{{ row.description }}</td>
            <td class="value-col">{{ row.get_formatted("tax_amount") }}</td>
        </tr>
        {% endif %}
        {% endfor %}

        {% if doc.discount_amount %}
        <tr>
            <td class="label-col">Discount</td>
            <td class="value-col" style="color:#ef4444;">- {{ doc.get_formatted("discount_amount") }}</td>
        </tr>
        {% endif %}

        <tr class="grand-total-row">
            <td class="label-col" style="padding-top:15px;">Total</td>
            <td class="grand-total">{{ doc.get_formatted("grand_total") }}</td>
        </tr>
    </table>
</div>

{% if doc.terms %}
<div class="terms-section">
    <h4>Terms & Conditions</h4>
    <p>{{ doc.terms | replace('\n', '<br>') }}</p>
</div>
{% endif %}
    """

    # Check if Print Format Exists
    pf_name = "Vinfork Zoho Style"
    if not frappe.db.exists("Print Format", pf_name):
        pf = frappe.new_doc("Print Format")
        pf.name = pf_name
        pf.doc_type = "Sales Order"
        pf.module = "Vinfork Custom"
        pf.standard = "No"
        pf.custom_format = 1
        pf.print_format_type = "Jinja"
        pf.html = html_content
        pf.save()
        print(f"✅ Created Print Format: {pf_name}")
    else:
        # Update existing
        pf = frappe.get_doc("Print Format", pf_name)
        pf.html = html_content
        pf.save()
        print(f"🔄 Updated Print Format: {pf_name}")

    frappe.db.commit()
