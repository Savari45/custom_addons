/** @odoo-module */

import { useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { Dialog } from "@web/core/dialog/dialog";
import { useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component } from "@odoo/owl";
import { UpdateStockOnHandLocationPopup } from "@adevx_pos_product_management/js/UpdateStockOnHandLocationPopup";


export class UpdateStockOnHandPopup extends Component {

    static components = { UpdateStockOnHandLocationPopup, Dialog }
    static template = "adevx_pos_product_management.UpdateStockOnHandPopup"
    static props = ['close'];

    static defaultProps = {
        confirmText: _t("Save"),
        cancelText: _t("Close"),
        body: "",
        cancelKey: false,
    };

    setup() {
        super.setup();
        this.pos = usePos();
        this.dialog =  useService("dialog");
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.currentOrder = this.pos.get_order();
        this._id = 0;
        this.state = useState({
            array: this._initialize(this.props.array)
        });
    }

    _nextId() {
        return this._id++;
    }

    _emptyItem() {
        return {
            lot_id: null, quantity: 0, location_id: 0, _id: this._nextId(),
        };
    }

    _initialize(array) {
        if (array.length === 0) return [this._emptyItem()];
        return array.map((item) => Object.assign({}, {_id: this._nextId()}, typeof item === 'object' ? item : {
            'quantity': item.quantity,
            'location_id': item.location_id,
            'lot_id': item.lot_id
        }));
    }

    removeItem(itemToRemove) {
        this.state.array.splice(this.state.array.findIndex(item => item._id == itemToRemove._id), 1);
        if (this.state.array.length === 0) {
            this.state.array.push(this._emptyItem());
        }
    }

    createNewItem() {
        if (this.props && this.props.isSingleItem) return;
        this.state.array.push(this._emptyItem());
        this.render()
    }

    get_newStockArray() {
        return {
            newArray: this.state.array
                .filter((item) => item.quantity != 0 && item.location_id > 0)
                .map((item) => Object.assign({}, item)),
        };
    }
    async _loadStock(productId) {
        let qty_available = 0;
        let currentStockLocation = this.pos.default_location_src_id
        const product_onhand_per_location = await this.orm.call("stock.location", "get_stock_datas_by_locationIds", [[productId], [currentStockLocation]])
        if (product_onhand_per_location && product_onhand_per_location[currentStockLocation] && product_onhand_per_location[currentStockLocation][productId]) {
            qty_available = product_onhand_per_location[currentStockLocation][productId]
        }
        this.props.product.qty_available = qty_available ;
    }

    async OnConfirmUpdateQty(){
        const newStockArray = this.get_newStockArray()['newArray']
        console.log(newStockArray)
        let product = this.props.product;
        for (let i = 0; i < newStockArray.length; i++) {
            let newStock = newStockArray[i];
            if (!this.props.withLot) {
                let location_id = parseInt(newStock['location_id'])
                let vals = {
                    product_id: product.id,
                    product_tmpl_id: product.product_tmpl_id,
                    quantity: parseFloat(newStock['quantity']),
                    location_id: location_id
                }
                console.log("vals",vals)
                await this.orm.call("stock.location", "pos_update_stock_on_hand_by_location_id", [[location_id], vals]);
            } else {
                let args = {
                    quantity: parseFloat(newStock['quantity']),
                }
                let location_id = parseInt(newStock['id'])
                await this.orm.call("stock.quant", "write", [location_id], args);
            }
        }
        this._loadStock(product.id)
        this.notification.add(product.display_name + _t(' Successfully update stock on hand'));
        this.props.close();
    }

}
