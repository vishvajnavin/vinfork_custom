# Copyright (c) 2024, vishvaj navin and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import add_days, getdate, nowdate

def execute(filters=None):
	if not filters: filters = {}
	columns = get_columns()
	data = get_data(filters, columns)
	return columns, data

def get_columns():
	# Standard Columns
	columns = [
		{
			"fieldname": "work_order",
			"label": "Work Order",
			"fieldtype": "Link",
			"options": "Work Order",
			"width": 120
		},
		{
			"fieldname": "sales_order",
			"label": "Sales Order",
			"fieldtype": "Link",
			"options": "Sales Order",
			"width": 120
		},
		{
			"fieldname": "planned_end_date",
			"label": "Due Date",
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "customer_name",
			"label": "Customer",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "production_item",
			"label": "Model / Item",
			"fieldtype": "Link",
			"options": "Item",
			"width": 150
		},
		{
			"fieldname": "qty",
			"label": "Qty",
			"fieldtype": "Int",
			"width": 50
		}
	]
	
	# Dynamic Columns for Operations
	# Fetch all active operations to create columns
	active_ops = frappe.get_all("Operation", fields=["name"], order_by="idx asc, name asc")
	
	for op in active_ops:
		columns.append({
			"fieldname": frappe.scrub(op.name) + "_status", # e.g. "frame_making_status"
			"label": op.name,
			"fieldtype": "Data",
			"width": 110
		})

	# Overall Status Field
	columns.append({
		"fieldname": "overall_status",
		"label": "Status",
		"fieldtype": "Data",
		"width": 100
	})
	
	return columns

def get_data(filters, columns):
	# 1. Logic: Fetch Work Orders
	# - Show all Open/In Process
	# - Show Completed ONLY if completed within last 7 days
	
	conditions = ""
	if filters.get("from_date") and filters.get("to_date"):
		conditions += f" AND planned_start_date BETWEEN '{filters.get('from_date')}' AND '{filters.get('to_date')}'"

	wos = frappe.db.sql(f"""
		SELECT 
			name as work_order, sales_order, production_item, qty, 
			status, planned_end_date, actual_end_date, company
		FROM `tabWork Order`
		WHERE docstatus = 1 {conditions}
		ORDER BY planned_end_date ASC
	""", as_dict=1)

	# 7-Day Retention Logic for Completed Orders
	today = getdate(nowdate())
	seven_days_ago = add_days(today, -7)
	
	filtered_wos = []
	for wo in wos:
		if wo.status == "Completed":
			# If completed before 7 days ago, skip it
			if wo.actual_end_date and getdate(wo.actual_end_date) < seven_days_ago:
				continue
		filtered_wos.append(wo)

	if not filtered_wos:
		return []

	wo_names = [d.work_order for d in filtered_wos]
	
	# 2. Fetch Customer Info
	so_customer_map = {}
	if wo_names:
		sales_orders = [d.sales_order for d in filtered_wos if d.sales_order]
		if sales_orders:
			res = frappe.db.get_all("Sales Order", filters={"name": ["in", sales_orders]}, fields=["name", "customer_name"])
			for r in res:
				so_customer_map[r.name] = r.customer_name

	# 3. Fetch Job Cards
	# We need operation, status, docstatus
	job_cards = frappe.db.get_all("Job Card", 
		filters={"work_order": ["in", wo_names], "docstatus": ["!=", 2]},
		fields=["work_order", "operation", "status", "docstatus"])
	
	# Group Job Cards by Work Order AND Operation
	# jc_map[work_order][operation_name] = [list of cards]
	jc_map = {}
	for jc in job_cards:
		if jc.work_order not in jc_map:
			jc_map[jc.work_order] = {}
		
		# Normalize operation name key
		if jc.operation not in jc_map[jc.work_order]:
			jc_map[jc.work_order][jc.operation] = []
			
		jc_map[jc.work_order][jc.operation].append(jc)

	# 4. Construct Rows
	active_ops_list = frappe.get_all("Operation", fields=["name"], order_by="idx asc, name asc")
	
	data = []
	for wo in filtered_wos:
		row = {
			"work_order": wo.work_order,
			"sales_order": wo.sales_order,
			"planned_end_date": wo.planned_end_date,
			"customer_name": so_customer_map.get(wo.sales_order, ""),
			"production_item": wo.production_item,
			"qty": wo.qty,
		}
		
		# Logic for Each Operation Column
		total_ops_count = 0
		completed_ops_count = 0
		started_ops_count = 0
		
		wo_cards = jc_map.get(wo.work_order, {})
		
		for op in active_ops_list:
			field_name = frappe.scrub(op.name) + "_status"
			
			# Find Job Cards for this specific Operation
			# Be careful with exact string matching logic if names vary slightly
			# Here we assume exact match on 'operation' link field
			cards = wo_cards.get(op.name, [])
			
			status_text = "Not Started" # Default
			
			if not cards:
				# No job card created for this op yet
				status_text = "Not Started"
			else:
				total_ops_count += 1
				
				# Analyze Status
				# Priority: Done > WIP > Not Started (Open)
				
				all_done = all(c.docstatus == 1 or c.status == "Completed" for c in cards)
				any_wip = any(c.status == "Work In Progress" for c in cards)
				
				if all_done:
					status_text = "Done"
					completed_ops_count += 1
				elif any_wip:
					status_text = "WIP"
					started_ops_count += 1
				else:
					# Cards exist (Open) but none started
					status_text = "Not Started"
			
			row[field_name] = status_text

		# Logic for Overall Status
		# If ALL Ops are "Not Started" -> "Not Started"
		# If ANY Op is "WIP" or "Done" (but not all) -> "WIP"
		# If ALL Ops are "Done" -> "Completed"
		# Note: We rely on 'total_ops_count' tracking ONLY the ops that physically exist as job cards
		# If no job cards exist at all yet:
		
		overall = "Not Started"
		
		if wo.status == "Completed":
			overall = "Completed"
		else:
			if total_ops_count > 0:
				if completed_ops_count == total_ops_count:
					overall = "Completed"
				elif completed_ops_count > 0 or started_ops_count > 0:
					overall = "WIP"
				else:
					overall = "Not Started"
			else:
				# No job cards -> Check WO status
				if wo.status == "In Process":
					overall = "WIP"
				else:
					overall = "Not Started"
					
		row["overall_status"] = overall
		data.append(row)

	return data

