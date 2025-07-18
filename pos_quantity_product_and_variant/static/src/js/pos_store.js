import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";


patch(PosStore.prototype, {
    async processProductAttributes() {
		await super.processProductAttributes();
        this.available_product_id_quantities = await this.data.call("pos.session", "get_available_product_quantities", [[this.session.id]]);
        this.product_mapping = await this.data.call("pos.session", "get_product_mapping", [[this.session.id]]);
        this.product_info = await this.data.call("pos.session", "get_product_info", [[this.session.id]]);
        this.quick_link_product = NaN;
	},

    async openConfigurator(product) {
        if (this.quick_link_product) {
            const product = this.quick_link_product;
            this.quick_link_product = NaN;

            let attribute_value_ids = [];
            var price_extra = 0.0;

            product.product_template_variant_value_ids.forEach((attribute_component) => {
                attribute_value_ids.push(attribute_component.id);
                const attr = this.data.models["product.template.attribute.value"].get(attribute_component.id);
                if (attr && attr.attribute_id.create_variant !== "always") {
                    price_extra += attribute_value_ids.price_extra;
                }
            })
            return {
                attribute_value_ids: attribute_value_ids,
                attribute_custom_values: [],
                price_extra: price_extra,
                quantity: 1,
            }; 
        }
        return await super.openConfigurator(product);
    }
});