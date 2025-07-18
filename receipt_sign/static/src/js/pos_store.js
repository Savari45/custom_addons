/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    setup() {
        super.setup();
        console.log("[Store] POS Store patched");
    },

    async _processData(loadedData) {
        await super._processData(...arguments);
        console.log("[Store] Processed data:", loadedData);
        return loadedData;
    }
});