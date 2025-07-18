/** @odoo-module */

import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { patch } from "@web/core/utils/patch";
const { onMounted } = owl

patch(ReceiptScreen.prototype, {
    setup() {
        super.setup(...arguments);
        
        onMounted(async () => {
            if(this.pos.config.send_auto_email){
                if(/^.+@.+$/.test(this.state.email)){
                    this.actionSendReceiptOnEmail()
                }
            }
        })
    },
})