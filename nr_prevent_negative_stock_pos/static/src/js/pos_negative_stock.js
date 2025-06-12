/** @odoo-module **/

import {AlertDialog} from "@web/core/confirmation_dialog/confirmation_dialog";
import {PosStore} from "@point_of_sale/app/store/pos_store";
import {_t} from "@web/core/l10n/translation";
import {patch} from "@web/core/utils/patch";
import {rpc} from "@web/core/network/rpc";

patch(PosStore.prototype, {
    async addLineToOrder(vals, order, opts = {}, configure = true) {
        const product =
            typeof vals.product_id === "number"
                ? this.data.models["product.product"].get(vals.product_id)
                : vals.product_id;

        // Product check for consu type and stock
        if (product?.type === "consu") {
            const result = await rpc("/web/dataset/call_kw/product.product/read", {
                model: "product.product",
                method: "read",
                args: [[product.id], ["qty_available", "display_name"]],
                kwargs: {},
            });

            const available = result?.[0]?.qty_available || 0;
            const requestedQty = vals.qty || 1;

            // Get quantity already added for this product in the current order
            const currentOrder = this.get_order();
            const existingQty = currentOrder
                .get_orderlines()
                .filter((line) => line.product_id?.id === product.id)
                .reduce((sum, line) => sum + line.get_quantity(), 0);

            const totalQty = existingQty + requestedQty;

            if (available < totalQty) {
                this.dialog.add(AlertDialog, {
                    title: _t("No Stock Available"),
                    body: _t(
                        `Product "${product.display_name}" has insufficient stock.\n` +
                            `Available: ${available}, In Cart: ${existingQty}, Attempted to Add: ${requestedQty}`
                    ),
                });

                return;
            }
        }

        await super.addLineToOrder(vals, order, opts, configure);
    },
});
