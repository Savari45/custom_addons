/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { OrderWidget } from "@point_of_sale/app/generic_components/order_widget/order_widget";

import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { usePos } from "@point_of_sale/app/store/pos_hook";

patch(OrderWidget.prototype, {
    setup() {
        super.setup()
        this.pos = usePos();
    },
    getMargin(){
        const order = this.env.services.pos.get_order();
        const margin = order ? order.get_total_margin() : 0;
        return this.env.utils.formatCurrency(margin);
    },
    getMarginPercentage(){
        const order = this.env.services.pos.get_order();
        const percent = order ? order.get_total_margin_percent() : 0;
        return `${percent.toFixed(2)}%`;
    },

});


patch(Orderline.prototype, {
    setup() {
        super.setup(...arguments);
        this.pos = usePos();
    },
});