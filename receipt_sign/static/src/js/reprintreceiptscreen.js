/** @odoo-module **/

import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { patch } from "@web/core/utils/patch";

const PosReceiptScreenPatch = {
    setup() {
        super.setup();
        console.log("ReceiptScreen setup patched");
    },
};

patch(ReceiptScreen.prototype, PosReceiptScreenPatch);