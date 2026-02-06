frappe.ui.form.on('Work Order', {
    setup: function (frm) {
        if (frm.is_new()) {
            frm.set_value('skip_transfer', 1);
        }
    },
    onload: function (frm) {
        if (frm.is_new()) {
            // Force it again with a small delay to ensure it beats standard scripts
            setTimeout(() => {
                frm.set_value('skip_transfer', 1);
            }, 500);
        }
    },
    refresh: function (frm) {
        // 1. Fetch Sales Order Details (Custom Fields) - REMOVED per user request


        // 2. BOM Update Tool (Only if Completed)
        if (frm.doc.status === "Completed" && frm.doc.bom_no) {

            // Use add_inner_button -> This puts it clearly in the top right menu
            frm.page.add_inner_button(__('Update BOM from Actuals'), function () {
                frappe.confirm(
                    'This will Cancel the current Shell BOM and create a new Standard BOM based on the materials you used in this order. Proceed?',
                    function () {
                        frappe.call({
                            method: "vinfork_custom.bom_update_tool.update_bom_from_actuals",
                            args: {
                                work_order_name: frm.doc.name
                            },
                            freeze: true,
                            freeze_message: "Updating BOM...",
                            callback: function (r) {
                                if (!r.exc) {
                                    frappe.msgprint("BOM Updated Successfully: " + r.message);
                                    frm.reload_doc();
                                }
                            }
                        });
                    }
                );
            });

            // Add a visual indicator color (Primary)
            frm.page.set_inner_btn_primary('Update BOM from Actuals');
        }
    }
});
