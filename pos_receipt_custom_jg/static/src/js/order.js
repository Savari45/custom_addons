/* @odoo-modules */

import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";
const formatCurrency = registry.subRegistries.formatters.content.monetary[1];

patch(PosOrder.prototype, {
    /**
     * Checks if the current line applies for a global discount from `pos_discount.DiscountButton`.
     * @returns Boolean
     */


    get_total_discount() {
        var total_discount = super.get_total_discount() || 0;
        const product = this.config.discount_product_id?.id;        
        const lines = this.lines;
        
        var global_discount = 0;
        if (lines) {
            for (let i = 0; i < lines.length; i++) {
                const line = lines[i];
                const lineProduct = line.get_product();
                const lineProductId = lineProduct?.id;
                
                // Check the matching conditions
                const matchesConfigProduct = (lineProductId === product);
                const matchesHardcodedId = (lineProductId === 34685);
                
                if (matchesConfigProduct) {
                    const linePrice = line.get_display_price();
                    global_discount -= linePrice;
                } else if (matchesHardcodedId) {
                    const linePrice = line.get_display_price();
                    global_discount -= linePrice;
                }
            }
        } else {
            console.log("No orderlines found to process");
        }
        
        console.log("Calculated global_discount:", global_discount);
        // Add global_discount to total_discount
        total_discount += global_discount;
        console.log("Final total_discount after adding global_discount:", total_discount);
        
        return total_discount;
    },



    export_for_printing(baseUrl, headerData) {
        var ret = super.export_for_printing(...arguments);
        // Calculate total without discount
        ret.total_without_discount = ret.total_without_tax + ret.total_discount;
        var customer = this.get_partner_name();
        
        // Format currency values
        ret.total_without_discount_formatted = formatCurrency(ret.total_without_discount);
        ret.total_discount_formatted = formatCurrency(ret.total_discount);
        ret.amount_total_formatted = formatCurrency(ret.amount_total);
        ret.total_paid_formatted = formatCurrency(ret.total_paid);
        ret.change_formatted = formatCurrency(ret.change);
        ret.customer = customer;
        return ret;
    }
});