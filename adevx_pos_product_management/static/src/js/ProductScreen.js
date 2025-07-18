/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";

patch(ProductScreen.prototype, {

     async addProductToOrder(product) {
        super.addProductToOrder(...arguments)
         if (product.type == 'consu'){
            product.qty_available -= 1;
        }
    }

});
