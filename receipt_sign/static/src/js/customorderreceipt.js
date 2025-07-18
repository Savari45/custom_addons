/** @odoo-module **/
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { patch } from "@web/core/utils/patch";

patch(OrderReceipt.prototype, {
    setup() {
        super.setup();
        console.log("[Receipt] Order:", this.props.order);
        console.log("[Receipt] Signature code available:", 'signature_code' in this.props.order);
    }
});