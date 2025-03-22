/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Many2OneField } from "@web/views/fields/many2one/many2one_field";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { Component, useState } from "@odoo/owl";

// ✅ Register Many2OneField as a custom field
registry.category("fields").add("m2o_product_wizard", Many2OneField);

// ✅ Patch Many2OneField to Add Custom Behavior
patch(Many2OneField.prototype, {
    get Many2XAutocompleteProps() {
        const props = super.Many2XAutocompleteProps;
        props.quickCreate = this.openConfirmationDialog.bind(this);
        return props;
    },

    async openConfirmationDialog() {
        if (!this.inputValue || this.inputValue.trim() === "") {
            console.warn("No input value for product creation.");
            return;
        }

        const dialogService = this.env.services.dialog;
        if (!dialogService) {
            console.error("Dialog service is not available.");
            return;
        }

        dialogService.add(ConfirmProductDialog, {
            title: "Create New Product?",
            message: `Do you want to create '${this.inputValue}' as a new product?`,
            onConfirm: () => console.log("✅ Product created:", this.inputValue),
            onCancel: () => console.log("❌ Product creation canceled"),
        });
    }
});

// ✅ Define OWL Dialog Component Properly
class ConfirmProductDialog extends Component {
    static template = "custom_purchase_order_line.PurchaseProductDialog";

    static props = { title: String, message: String, onConfirm: Function, onCancel: Function };

    setup() {
        this.dialog = useService("dialog");
    }

    confirm() {
        this.props.onConfirm();
        this.dialog.close();
    }

    cancel() {
        this.props.onCancel();
        this.dialog.close();
    }
}

// ✅ Register the Dialog Component in Odoo
registry.category("components").add("ConfirmProductDialog", ConfirmProductDialog);
