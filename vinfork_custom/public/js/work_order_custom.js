frappe.ui.form.on('Work Order', {
    refresh: function (frm) {
        // Debugging Logs
        console.log("VINFORK DEBUG: Work Order Script Loaded");
        console.log("VINFORK DEBUG: Status =", frm.doc.status);
        console.log("VINFORK DEBUG: BOM No =", frm.doc.bom_no);

        // Only show if Completed and has a BOM
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
