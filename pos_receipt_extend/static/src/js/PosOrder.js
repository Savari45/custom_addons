import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {
    export_for_printing(baseUrl, headerData) {
        const result = super.export_for_printing(...arguments);
        result.headerData = result.headerData || {};
        result.invoice_number = this.account_move_name || "";
        result.signature_code= this.account_move_code || "";

        result.headerData.invoice_no =  result.invoice_number;

        result.headerData.signature_code = result.signature_code
        const orderlines = this.get_orderlines();
       // Extract and structure tax details
        result.orderlines = orderlines.map((line) => {
            const base_price = line.get_base_price ? line.get_base_price() : 0;
            const prices = line.get_all_prices ? line.get_all_prices() : { taxesData: [] };

            const tax_list = (prices.taxesData || []).map((taxData) => ({
                name: taxData.tax.name,
                amount: taxData.amount,
                rate: base_price
                    ? ((taxData.amount / base_price) * 100).toFixed(2) + "%"
                    : "0.00%",
            }));

            return {
                id: line.id,
                product_name: line.get_product().display_name,
                quantity: line.get_quantity(),
                price: line.get_unit_price(),
                discount: line.get_discount(),
                line_total: line.get_quantity() * line.get_unit_price() * (1 - line.get_discount() / 100),
                line_taxes: tax_list,
            };
        });

        // Add partner details
        const partner = this.get_partner();
        if (partner) {
            result.headerData.customer_name = partner.name || "";
            result.headerData.customer_address = partner.contact_address || "";
            result.headerData.customer_mobile = partner.mobile || "";
            result.headerData.customer_phone = partner.phone || "";
            result.headerData.customer_email = partner.email || "";
            result.headerData.customer_vat = partner.vat || "";
        }


        return result;
    },
});