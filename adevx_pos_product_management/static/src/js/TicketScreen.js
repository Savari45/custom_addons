/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";

patch(TicketScreen.prototype, {


     getToRefundDetail(orderline) {
        let res = super.getToRefundDetail(...arguments);
        if (orderline) {
            orderline.product_id.qty_available += orderline.qty;
        }
        return res;
    }

});
