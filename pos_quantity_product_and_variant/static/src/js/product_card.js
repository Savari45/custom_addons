import { ProductCard } from "@point_of_sale/app/generic_components/product_card/product_card";
import { patch } from "@web/core/utils/patch";
import { usePos } from "@point_of_sale/app/store/pos_hook";


patch(ProductCard.prototype, {
    setup(){
        super.setup()
        this.pos = usePos();
    },
    get order_product_qty() {
        let orderProductQty = {};
        let order_list = this.pos.get_open_orders();
        for (let i = 0; i < order_list.length; i++) {
            const order = order_list[i];
            const orderlines = order.get_orderlines();            
            for (let j = 0; j < orderlines.length; j++) {
                const orderLine = orderlines[j];
                if (orderLine.product_id) {
                    const productId = orderLine.product_id.id;
                    const quantity = orderLine.qty;

                    if (!orderProductQty[productId]) {
                        orderProductQty[productId] = 0;
                    }
                    orderProductQty[productId] += quantity;
                }
            }
        }
        return orderProductQty;
    },
    available_variants_product_tmpl_qty(product_id) {
        if (!product_id) {return []; }
        const product_tmpl_id = this.pos.product_mapping[product_id.toString()];
        if (!product_tmpl_id) {return [];}
        return this.pos.available_product_id_quantities[product_tmpl_id.toString()] || [];    
    },
    get order_product_tmpl_qty() {
        let orderProductQty = {};
        let order_list = this.pos.get_open_orders();
        for (let i = 0; i < order_list.length; i++) {
            const order = order_list[i];
            const orderlines = order.get_orderlines();            
            for (let j = 0; j < orderlines.length; j++) {
                const orderLine = orderlines[j];
                if (orderLine.product_id) {
                    const product_tmpl_id = this.pos.product_mapping[orderLine.product_id.id.toString()];
                    const quantity = orderLine.qty;

                    if (!orderProductQty[product_tmpl_id]) {
                        orderProductQty[product_tmpl_id] = 0;
                    }
                    orderProductQty[product_tmpl_id] += quantity;
                }
            }
        }
        return orderProductQty;
    },
    select_product_variant(product_id) {
        this.pos.quick_link_product = this.pos.models["product.product"].get(product_id)
    }
});
