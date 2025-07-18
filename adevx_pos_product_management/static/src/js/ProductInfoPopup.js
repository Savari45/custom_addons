/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { ProductInfoPopup } from "@point_of_sale/app/screens/product_screen/product_info_popup/product_info_popup";

patch(ProductInfoPopup.prototype, {

    _hasMarginsCostsAccessRights() {
        // function recode
        const isAccessibleToEveryUser = this.pos.config.is_margins_costs_accessible_to_every_user;
        return isAccessibleToEveryUser;
    }

});
