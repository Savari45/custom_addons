/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { OrderSummary } from "@point_of_sale/app/screens/product_screen/order_summary/order_summary";

patch(OrderSummary.prototype, {


    _setValue(val) {
        const { numpadMode } = this.pos;
        let selectedLine = this.currentOrder.get_selected_orderline();
        if (selectedLine && val != 'remove') {
            if (numpadMode === "quantity") {
                let reserved_qty = ((val || 0) - selectedLine.qty);
                selectedLine.product_id.qty_available -= reserved_qty;
                if (selectedLine.product_id.qty_available < 0 && !this.pos.config.allow_order_out_of_stock && selectedLine.product_id.type == 'consu'){
                    selectedLine.product_id.qty_available += reserved_qty;
                    val = selectedLine.qty + selectedLine.product_id.qty_available;
                    this.pos.notification.add(
                        _t('Product Out of Stock: Only %s Available added', selectedLine.product_id.qty_available), 3000);
                    selectedLine.product_id.qty_available = 0;
                }
            }
        }
        return super._setValue(val);
    }

});
