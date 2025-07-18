/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ProductOnHand } from "@adevx_pos_product_management/js/ProductOnHand";
import { ProductCard } from "@point_of_sale/app/generic_components/product_card/product_card";

ProductCard.components = { ProductOnHand }

patch(ProductCard.prototype, {

    setup() {
        super.setup();
        this.pos = usePos();
    },

    get _allowDisplayOnhand() {
        let product = this.props.product;
        if (this.pos.config.display_onhand && this.pos.default_location_src_id && product['type'] === 'consu') {
            return true
        } else {
            return false
        }
    },


});
