/** @odoo-module **/

import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {
    export_for_printing() {
        const result = super.export_for_printing(...arguments);
        result.headerData = result.headerData || {};
        console.log('result.headerDate',result.headerData)
        if (this.signature_code) {
            result.headerData.signature_code = this.signature_code;
              console.log('result.headerDate',result.headerData.signature_code)
        }
        return result;
    },
});
