/** @odoo-module */

import { patch} from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    async processServerData() {
        await super.processServerData();

        this.stock_locations = this.models["stock.location"].getFirst();
        this.product_attributes = this.models["product.attribute"].getFirst();
        this.product_attribute_values = this.models["product.attribute.value"].getFirst();
        this.product_template_attribute_values = this.models["product.template.attribute.value"].getFirst();

        this.default_location_src_id = this.config.picking_type_id.default_location_src_id.id;

        this.stock_location_by_id = {};
        this.stock_location_ids = [];
        this.updated_stock_locations = [];
        if (this.stock_locations){
            for (const [key, loc] of Object.entries(this.stock_locations.baseData)) {
                this.stock_location_by_id[loc.id] = loc;
                this.stock_location_ids.push(loc.id);
                this.updated_stock_locations.push(loc);
            }
        }

        this.product_attribute_by_id = {};
        if (this.product_attributes){
            for (const [key, attr] of Object.entries(this.product_attributes.baseData)) {
                 this.product_attribute_by_id[attr.id] = attr;
            }
        }

        this.product_template_attribute_values_by_product_tmpl_id = {};
        if (this.product_template_attribute_values){
            for (const [key, tmpl_attr] of Object.entries(this.product_template_attribute_values.baseData)) {
                let tmpl_attr_tmpl_attr_product_tmpl_id = tmpl_attr.product_tmpl_id[0]
                if (this.product_template_attribute_values_by_product_tmpl_id.hasOwnProperty(tmpl_attr_tmpl_attr_product_tmpl_id)){
                    this.product_template_attribute_values_by_product_tmpl_id[tmpl_attr.product_tmpl_id[0]].push(tmpl_attr)
                } else{
                    this.product_template_attribute_values_by_product_tmpl_id[tmpl_attr.product_tmpl_id[0]] = [tmpl_attr];
                }
            }
        }

        this.product_attribute_value_by_id = {};
        if (this.product_attribute_values){
            for (const [key, attr_val] of Object.entries(this.product_attribute_values.baseData)) {
                this.product_attribute_value_by_id[attr_val.id] = attr_val;
            }
        }

    },

    async pay() {

        var products_out_of_stock  = await this._checkQtyAvailable();
        if (products_out_of_stock.length > 0){
            this.notification.add(
                _t('Products Out of Stock %s', products_out_of_stock.toString()), 3000);
                return false;
        }
        return super.pay(...arguments);
    },

    async _checkQtyAvailable(){
        var products_out_of_stock = [];
        const order = this.get_order();
        if (!this.config.allow_order_out_of_stock){
            for (const line of order.lines.filter((l) => l.product_id.type == 'consu')){
                const product_onhand_per_location = await this.data.call("stock.location", "get_stock_datas_by_locationIds", [[line.product_id.id], [this.default_location_src_id]])
                const product_qty = product_onhand_per_location[this.default_location_src_id][line.product_id.id]
                if (line.qty > 0 && product_qty <= 0){
                    products_out_of_stock.push(line.product_id.display_name)
                }
            }
        }
        return products_out_of_stock;
    },


    orders_product_quantity_by_product_id() {
        let result = {};
        let order = this.get_order()
        for (const line of order.lines){
            if (result.hasOwnProperty(line.product_id.id)){
                result[line.product_id.id] += line.qty;
            }else{
                result[line.product_id.id] = line.qty;
            }
        }
        return result;
    }

});
