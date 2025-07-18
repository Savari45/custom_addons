import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { floatIsZero, roundPrecision as round_pr } from "@web/core/utils/numbers";

patch(PosOrder.prototype, {

    setup() {
        super.setup(...arguments);
    },

    
    get_total_margin() {
        return round_pr(
            this.lines.reduce((sum, orderLine) => sum + (orderLine.margin || 0), 0),
            this.currency.rounding
        );
    },
    get_total_margin_percent() {
        const margin = this.get_total_margin();
        const total_with_tax = this.get_total_with_tax();
        return total_with_tax > 0 ? (margin / total_with_tax) * 100 : 0;
   },
});

patch(PosOrderline.prototype, {

    setup() {
        super.setup(...arguments);
        this.set_staystr();
        this.set_orderline_margin(); 
    },
    set_quantity(qty, keep_price) {
        const result = super.set_quantity(qty, keep_price);
        this.set_orderline_margin();  // <- update margin
        return result;
    },
    set_unit_price(price) {
        const res = super.set_unit_price(price);
        this.set_orderline_margin();
        return res;
    },

    set_discount(discount) {
        const res = super.set_discount(discount);
        this.set_orderline_margin();
        return res;
    },


    getDisplayData() {
       const loaded = super.getDisplayData(...arguments);
       loaded['custom_margin'] = this.margin;
       loaded['custom_margin_percent'] = this.margin_percent;
       return loaded;
    },


    clone(){
        const orderline = super.clone(...arguments);
        orderline.margin = this.margin;
        orderline.margin_percent = this.margin_percent;
        return orderline;
    },
    set_staystr(){
        return this.margin;
    },
    set_orderline_margin(){
        const product_price = this.get_display_price(); // unit selling price
        const cost = this.product_id.standard_price || 0;    // unit cost price
        const product_qty = this.qty;                   // quantity ordered
        var temp_price = product_price / product_qty
        // Always recalculate margin fresh
        var margin = 0.0
        margin = (temp_price - cost) * product_qty;
        this.margin = margin;

        const total_selling = temp_price * product_qty;
        this.margin_percent = total_selling > 0 ? round_pr((margin / total_selling) * 100, 2) : 0;

        return margin;
    }
});

patch(Orderline, {
    props: {
        ...Orderline.props,
        line: {
            ...Orderline.props.line,
            shape: {
                ...Orderline.props.line.shape,
                custom_margin: { type: Number, optional: true },
                custom_margin_percent: { type: Number, optional: true },
            },
        },
    },
});