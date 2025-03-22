/** @odoo-module **/

import { Many2OneField } from "@web/views/fields/many2one/many2one_field";
import { patch } from "@web/core/utils/patch";

patch(Many2OneField.prototype, {
  get Many2XAutocompleteProps() {
    const props = super.Many2XAutocompleteProps;

    // Apply customization only when the field is "product_id" inside "purchase.order.line"
    if (this.props.name === "product_id" && this.props.record.resModel === "purchase.order.line") {
      props.quickCreate = this.openConfirmationDialog.bind(this);
    }

    return props;
  },
});
