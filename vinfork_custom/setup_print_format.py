import frappe

def execute():
    """
    Installs the 'Vinfork Zoho Style' Print Format for Sales Order.
    Run via: bench execute vinfork_custom.setup_print_format.execute
    """
    
    # HTML Template (Zoho Style)
    html_content = """
<style>
    .print-format {
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
        color: #333;
        line-height: 1.5;
        font-size: 13px;
    }
    .header-section {
        margin-bottom: 30px;
        border-bottom: 1px solid #eee;
        padding-bottom: 20px;
    }
    .company-logo {
        max-height: 80px;
        max-width: 200px;
    }
    .doc-title {
        text-align: right;
        font-size: 24px;
        font-weight: bold;
        color: #333;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    .doc-status {
        text-align: right;
        font-size: 14px;
        color: #666;
    }
    .address-section {
        display: flex;
        justify-content: space-between;
        margin-bottom: 30px;
        gap: 20px;
    }
    .address-box h4 {
        font-size: 12px;
        color: #777;
        text-transform: uppercase;
        margin-bottom: 5px;
        font-weight: 600;
    }
    .items-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
    }
    .items-table th {
        background-color: #333;
        color: #fff;
        text-align: left;
        padding: 8px 10px;
        font-weight: 600;
        font-size: 11px;
        text-transform: uppercase;
    }
    .items-table td {
        border-bottom: 1px solid #eee;
        padding: 10px;
        vertical-align: middle;
    }
    .items-table tr:nth-child(even) {
        background-color: #fcfcfc;
    }
    .item-image {
        width: 100px;
        height: auto;
        object-fit: contain;
        border-radius: 4px;
        border: 1px solid #eee;
    }
    .total-section {
        display: flex;
        justify-content: flex-end;
    }
    .total-table {
        width: 40%;
        border-collapse: collapse;
    }
    .total-table td {
        padding: 5px 10px;
        text-align: right;
    }
    .total-table .label-col {
        color: #666;
    }
    .grand-total {
        font-size: 16px;
        font-weight: bold;
        border-top: 2px solid #333;
        padding-top: 10px !important;
    }
    .terms-section {
        margin-top: 40px;
        border-top: 1px solid #eee;
        padding-top: 10px;
        font-size: 11px;
        color: #777;
    }
</style>

<div class="header-section">
    <div class="row">
        <div class="col-xs-6">
            {% if doc.company_logo %}
                <img src="{{ doc.company_logo }}" class="company-logo">
            {% else %}
                <h2>{{ doc.company }}</h2>
            {% endif %}
        </div>
        <div class="col-xs-6 text-right">
            <div class="doc-title">Sales Order</div>
            <div class="doc-status"># {{ doc.name }}</div>
            <div class="doc-status">Date: {{ doc.get_formatted("transaction_date") }}</div>
        </div>
    </div>
</div>

<div class="address-section">
    <div class="address-box" style="width: 45%;">
        <h4>Bill To</h4>
        <div><strong>{{ doc.customer_name }}</strong></div>
        <div>{{ doc.billing_address_display or "" }}</div>
        {% if doc.contact_display %}
            <div style="margin-top:5px;">{{ doc.contact_display }}</div>
        {% endif %}
    </div>
    {% if doc.shipping_address_name != doc.customer_address %}
    <div class="address-box" style="width: 45%;">
        <h4>Ship To</h4>
        <div><strong>{{ doc.customer_name }}</strong></div>
        <div>{{ doc.shipping_address_display or "" }}</div>
    </div>
    {% endif %}
</div>

<table class="items-table">
    <thead>
        <tr>
            <th width="10%">Image</th>
            <th width="25%">Item</th>
            <th width="15%">Sofa Type</th>
            <th width="15%">Leather Range</th>
            <th width="5%" class="text-right">Qty</th>
            <th width="15%" class="text-right">Rate</th>
            <th width="15%" class="text-right">Amount</th>
        </tr>
    </thead>
    <tbody>
        {% for item in doc.items %}
        <tr>
            <td>
                {% if item.image %}
                    <img src="{{ item.image }}" class="item-image">
                {% else %}
                    <div style="width:50px; height:50px; background:#f0f0f0; border-radius:4px;"></div>
                {% endif %}
            </td>
            <td>
                <strong>{{ item.item_name }}</strong>
            </td>
            <td>
                {{ item.custom_sofa_type or frappe.db.get_value("Item", item.item_code, "custom_sofa_type") or "" }}
            </td>
            <td>
                {{ item.custom_sofa_config_copy or frappe.db.get_value("Item", item.item_code, "custom_sofa_config_copy") or "" }}
            </td>
            <td class="text-right">{{ item.qty }}</td>
            <td class="text-right">{{ item.get_formatted("rate") }}</td>
            <td class="text-right">{{ item.get_formatted("amount") }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>

<div class="total-section">
    <table class="total-table">
        <tr>
            <td class="label-col">Subtotal</td>
            <td>{{ doc.get_formatted("total") }}</td>
        </tr>
        
        {% for row in doc.taxes %}
        {% if not row.included_in_print_rate %}
        <tr>
            <td class="label-col">{{ row.description }}</td>
            <td>{{ row.get_formatted("tax_amount") }}</td>
        </tr>
        {% endif %}
        {% endfor %}

        {% if doc.discount_amount %}
        <tr>
            <td class="label-col">Discount</td>
            <td>- {{ doc.get_formatted("discount_amount") }}</td>
        </tr>
        {% endif %}

        <tr>
            <td class="label-col grand-total">Total</td>
            <td class="grand-total">{{ doc.get_formatted("grand_total") }}</td>
        </tr>
    </table>
</div>

{% if doc.terms %}
<div class="terms-section">
    <h4>Terms & Conditions</h4>
    <p>{{ doc.terms }}</p>
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
