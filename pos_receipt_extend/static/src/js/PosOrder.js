import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {
    export_for_printing(baseUrl, headerData) {
        const result = super.export_for_printing(...arguments);
        result.headerData = result.headerData || {};
        result.invoice_number = this.account_move_name || "";
        result.signature_code= this.account_move_code || "";
        console.log('invoice_number',result.invoice_number)
        console.log('signature_code',result.signature_code)
        result.headerData.invoice_no =  result.invoice_number;
        console.log('invoice number in the header', result.headerData.invoice_no)
        result.headerData.signature_code = result.signature_code
        console.log('invoice signature code ',  result.headerData.signature_code)


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