/** @odoo-module */
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
    async afterOrderValidation() {
        const orderlines = this.currentOrder.get_orderlines();
        for (let j = 0; j < orderlines.length; j++) {
            const orderLine = orderlines[j];
            if (orderLine.product_id) {
                orderLine.product_id.virtual_available -= orderLine.qty
                orderLine.product_id.qty_available -= orderLine.qty

                this.pos.product_info[orderLine.product_id.id]["virtual_available"] -= orderLine.qty
                this.pos.product_info[orderLine.product_id.id]["qty_available"] -= orderLine.qty
            }
        }
        return await super.afterOrderValidation();
    },
});
