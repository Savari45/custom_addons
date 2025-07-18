/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { Component, useExternalListener } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class UpdateStockOnHandLocationPopup extends Component {
    static template = "adevx_pos_product_management.UpdateStockOnHandLocationPopup"

    static props = ['*'];
    static defaultProps = {
        confirmText: _t("Save"),
        cancelText: _t("Close"),
        title: _t("Update stock on hand"),
        body: "",
        cancelKey: false,
    }

    setup() {
        super.setup();
        this.pos = usePos();
        useExternalListener(document, "keyup", this._onHotkeys);
    }

    _onHotkeys(event) {
        if (event.key === "Enter" && !this.props.withLot) {
            this.props.createNewItem()
        }
        if (event.key === "Backspace" && !this.props.withLot) {
            this.props.removeItem(this.props.item)
        }
    }
}
