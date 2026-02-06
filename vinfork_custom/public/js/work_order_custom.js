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
        // 1. Fetch Sales Order Details (Custom Fields)
        if (frm.doc.sales_order_item && !frm.doc.custom_sofa_type) {
            frappe.db.get_value('Sales Order Item', frm.doc.sales_order_item,
                ['custom_sofa_type', 'custom_sofa_config_copy', 'leather_colour', 'custom_spl_instruction', 'custom_configuration_', 'custom_drawing__measurements_'],
                (r) => {
                    if (r) {
                        frm.set_value('custom_sofa_type', r.custom_sofa_type);
                        frm.set_value('custom_sofa_config_copy', r.custom_sofa_config_copy);
                        frm.set_value('leather_colour', r.leather_colour);
                        frm.set_value('custom_spl_instruction', r.custom_spl_instruction);
                        frm.set_value('custom_configuration_', r.custom_configuration_);
                        frm.set_value('custom_drawing__measurements_', r.custom_drawing__measurements_);
                    }
                }
            );
        }

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
