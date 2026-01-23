frappe.ui.form.on('Purchase Order', {
    refresh: function (frm) {
        frm.trigger('toggle_cosmo_field');
    },

    supplier: function (frm) {
        frm.trigger('toggle_cosmo_field');
    },

    toggle_cosmo_field: function (frm) {
        var is_cosmo = frm.doc.supplier && frm.doc.supplier.toLowerCase().includes("cosmo");

        // 1. Hide/Show in the Grid View (List)
        frm.fields_dict['items'].grid.update_docfield_property('custom_customer_ref', 'hidden', is_cosmo ? 0 : 1);

        // 2. Refresh Grid
        frm.fields_dict['items'].grid.refresh();
    }
});

frappe.ui.form.on('Purchase Order Item', {
    form_render: function (frm, cdt, cdn) {
        // This triggers when the row "Edit" modal is opened
        var item = locals[cdt][cdn];
        var parent_supplier = frm.doc.supplier;

        if (parent_supplier && parent_supplier.toLowerCase().includes("cosmo")) {
            // Show in Modal
            frappe.utils.unhide_field('custom_customer_ref');
            // Note: in child table context, standard hide/unhide might vary, 
            // closest is accessing the dialog field if open, strictly dependent on grid logic often.
            // But 'form_render' allows manipulating the dialog fields.
        } else {
            // Hide in Modal
            frappe.utils.hide_field('custom_customer_ref');
        }
    }
});
