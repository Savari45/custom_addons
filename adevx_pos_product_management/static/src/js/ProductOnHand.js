/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { Component, onMounted, onWillUpdateProps, useState } from "@odoo/owl";
import { UpdateStockOnHandPopup } from "@adevx_pos_product_management/js/UpdateStockOnHandPopup";

export class ProductOnHand extends Component {
    static template = "adevx_pos_product_management.ProductOnHand";
    static props = ["*"];
    static defaultProps = {
        class: "",
    };

    setup() {
        super.setup();
        this.pos = usePos();
        this.product = this.props.product;
        this.dialog = useService("dialog");
        this.orm = useService("orm");
        this.notification = useService("notification");
        onMounted((nextProps) => {
            this._loadStock(this.props.productId);
        });
        onWillUpdateProps((nextProps) => {
            this._loadStock(nextProps.productId);
        });
    }

    get addedClasses() {
        if (this.product.qty_available > 0 && this.product.qty_available < 10) {
            return {
                'low-stock': true
            }
        } else if (this.product.qty_available >= 10) {
            return {
                'normal-stock': true
            }
        } else if (this.product.qty_available <= 0) {
            return {
                'out-of-stock': true
            }
        }
    }

    async _loadStock(productId) {
        let qty_available = 0;
        let currentStockLocation = this.pos.default_location_src_id

        const product_onhand_per_location = await this.orm.call("stock.location", "get_stock_datas_by_locationIds", [[productId], [currentStockLocation]])
        if (product_onhand_per_location && product_onhand_per_location[currentStockLocation] && product_onhand_per_location[currentStockLocation][productId]) {
            qty_available = product_onhand_per_location[currentStockLocation][productId]
        }
        let orders_product_qty = this.pos.orders_product_quantity_by_product_id()[productId] || 0;
        this.product.qty_available = qty_available - orders_product_qty;
    }

    async updateStockEachLocation() {
        if (!this.pos.config.update_stock_onhand) {
            return;
//            return this.dialog.add(ConfirmationDialog, {
//                title: _t('Error'), body: _t('Your POS not active feature Update Stock of Products')
//            })
        }
        let product = this.product;
        let stock_location_ids = this.pos.stock_location_ids
        let stock_datas = await this.orm.call("stock.location", "get_stock_datas_by_locationIds", [[product.id], stock_location_ids])
        if (stock_datas) {
            let items = [];
            let withLot = false
            if (product.tracking == 'lot') {
                withLot = true
            }
            if (!withLot) {
                for (let location_id in stock_datas) {
                    let location = this.pos.stock_location_by_id[location_id];
                    if (location) {
                        items.push({
                            id: location.id,
                            item: location,
                            location_id: location.id,
                            quantity: stock_datas[location_id][product.id]
                        })
                    }
                }
            }
            else {
                const args = {
                    domain: [["product_id", "=", product.id], ["location_id", "in", stock_location_ids]],
                    fields: ["lot_id", "location_id", "quantity"],
                    context: {
                        limit: 1
                    }
                }
                let stockQuants = await this.orm.call("stock.quant", "search_read", [], args);
                if (stockQuants) {
                    items = stockQuants.map((q) => ({
                        id: q.id,
                        item: q,
                        lot_id: q.lot_id[0],
                        lot_name: q.lot_id[1],
                        location_id: q.location_id[0],
                        location_name: q.location_id[1],
                        quantity: q.quantity
                    }));
                }
            }

            if (items.length) {
                await this.dialog.add(UpdateStockOnHandPopup, {
                    title: _t('Summary Stock on Hand (Available - Reserved) each Stock Location of [ ') + product.display_name + ' ]',
                    withLot: withLot,
                    array: items,
                    product: product,
                })
            } else {
                this.notification.add(_t('Warning. ') + product.display_name + _t(' not found stock on hand !!!'));
            }
        }
    }
}