/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { parseFloat as oParseFloat } from "@web/views/fields/parsers";
import { PosOrder } from "@point_of_sale/app/models/pos_order";


patch(PosOrder.prototype, {

    removeOrderline(line) {
        line.product_id.qty_available += line.qty;
        return super.removeOrderline(line);
    }

});

