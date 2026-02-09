"""
Work Order Hooks
Auto-start Work Orders on submission without creating stock entries
"""

import frappe

def auto_start_work_order(doc, method):
    """
    Auto-start Work Order after submission
    Runs via doc_events hook in hooks.py
    """
    if doc.status == "Not Started":
        # Use db_set to bypass validation on submitted documents
        frappe.db.set_value(
            "Work Order", 
            doc.name, 
            "status", 
            "In Process",
            update_modified=False
        )
        
        # Show success message
        frappe.msgprint(
            msg=f"✅ Work Order <b>{doc.name}</b> started automatically!<br><small>📌 Job Cards will be created when you click 'Create Job Card' button.</small>",
            title="Work Order Auto-Started",
            indicator="green"
        )
        
        # Commit the change
        frappe.db.commit()
