// static/src/js/pos_product_quantity_patch.js
/** @odoo-module **/

import { ProductCard } from "@point_of_sale/app/generic_components/product_card/product_card";
import { patch } from "@web/core/utils/patch";
import { useRef, onMounted } from "@odoo/owl";

patch(ProductCard.prototype, {
    setup() {
        super.setup();
        this.qty = this.props.product.available_qty_in_pos || 0.0;
        this.ref = useRef("productCard");

        onMounted(() => {
            const el = this.ref.el;
            if (el) {
                const info = document.createElement("div");
                info.innerText = `Qty: ${this.qty}`;
                info.style.fontSize = "12px";
                info.style.color = "black";
                info.style.marginTop = "2px";
                el.appendChild(info);
            }
        });
    },
});
