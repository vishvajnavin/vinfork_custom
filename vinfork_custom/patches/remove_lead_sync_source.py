
import frappe

def execute():
	doctype = "Lead Sync Source"

	# 1. Clean up Workspaces that reference the missing DocType
	if frappe.db.exists("Workspace"): # Only run if Workspace feature exists
		workspaces = frappe.get_all("Workspace", pluck="name")
		for w in workspaces:
			try:
				doc = frappe.get_doc("Workspace", w)
				modified = False
				
				# Iterate over links
				if hasattr(doc, "links"):
					new_links = []
					for link in doc.links:
						if link.link_to == doctype:
							modified = True
						else:
							new_links.append(link)
					
					if modified:
						doc.links = new_links
						doc.save()
						frappe.db.commit()

				# Iterate over shortcuts
				if hasattr(doc, "shortcuts"):
					new_shortcuts = []
					for shortcut in doc.shortcuts:
						if shortcut.link_to == doctype:
							modified = True
						else:
							new_shortcuts.append(shortcut)
					
					if modified:
						doc.shortcuts = new_shortcuts
						doc.save()
						frappe.db.commit()
			except Exception:
				# Log but don't crash
				frappe.log_error(f"Failed to patch workspace {w}")

	# 2. ALSO Check if the DocType record itself exists but file is missing
	# Often causing crashes if referenced by other things
	if frappe.db.exists("DocType", doctype):
		try:
			frappe.delete_doc("DocType", doctype, force=1)
		except Exception:
			# If delete_doc fails, allow manual removal or ignore
			pass
