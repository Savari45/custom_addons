/** @odoo-module */
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";

patch(PaymentScreen.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.pos = usePos();
    },

    async validateOrder(isForceValidate) {
        try {
            const receipt_order = await super.validateOrder(isForceValidate);
            const order = this.pos.get_order();

            // 🔁 Wait for backendId to be set (max 10 retries)
            let attempt = 0;
            while (!order.backendId && attempt < 10) {
                console.log(`⏳ Waiting for backendId... Try ${attempt + 1}`);
                await new Promise((resolve) => setTimeout(resolve, 500));
                attempt++;
            }

            if (!order.backendId) {
                console.warn("⚠️ Order has no backendId even after retries.");
                return receipt_order;
            }

            console.log("✅ Order synced, backend ID:", order.backendId);

            // 🔁 Wait for invoice to be created (max 5 retries)
            let tries = 0;
            let account_move_id = null;

            while (tries < 5 && !account_move_id) {
                const [order_data] = await this.orm.read(
                    'pos.order',
                    [order.backendId],
                    ['account_move']
                );
                account_move_id = order_data?.account_move?.[0];

                if (!account_move_id) {
                    console.log(`⏳ Try ${tries + 1}: Waiting for invoice creation...`);
                    await new Promise((resolve) => setTimeout(resolve, 500));
                    tries++;
                }
            }

            if (account_move_id) {
                const [invoice] = await this.orm.read(
                    'account.move',
                    [account_move_id],
                    ['name', 'invoice_date', 'amount_total', 'amount_tax', 'amount_untaxed', 'state', 'payment_state']
                );
                if (invoice) {
                    console.log("🧾 Invoice Data:", invoice);
                    order.invoice_data = invoice;
                    order.account_move = invoice;
                }
            } else {
                console.warn("⚠️ Invoice not created even after retries.");
            }

            return receipt_order;
        } catch (error) {
            console.error("❌ Error in validateOrder:", error);
            throw error;
        }
    },
});
