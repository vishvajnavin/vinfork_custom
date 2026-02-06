import frappe
from frappe.utils.pdf import get_pdf

@frappe.whitelist()
def download_custom_so_pdf(name):
    """
    Generates a PDF for the Sales Order and sets the filename to the Customer Name.
    """
    doc = frappe.get_doc("Sales Order", name)
    
    # Clean filename (remove illegal chars)
    filename = doc.customer_name.replace("/", "-").replace("\\", "-")
    filename = f"{filename}.pdf"

    # Get Print Format content
    # Using 'Vinfork Zoho Style' if exists, else standard
    print_format = "Vinfork Zoho Style" if frappe.db.exists("Print Format", "Vinfork Zoho Style") else "Standard"

    html = frappe.get_print("Sales Order", name, print_format=print_format)
    pdf_content = get_pdf(html)

    frappe.local.response.filename = filename
    frappe.local.response.filecontent = pdf_content
    frappe.local.response.type = "pdf"
