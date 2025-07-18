import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";


patch(ProductScreen.prototype, {
    // @override
	get productsToDisplay() {
        let productsToDisplay = super.productsToDisplay;

        if (this.pos.config.show_only_available_products) {
            const quantities_by_product_template = Object.keys(this.pos.available_product_id_quantities);
            productsToDisplay = productsToDisplay.filter((product) => {
                const product_tmpl_id = this.pos.product_mapping[product.id.toString()];
                if (quantities_by_product_template.includes(product_tmpl_id.toString())) {
                    return true;
                }
            });
        }
		return productsToDisplay;
    },
});