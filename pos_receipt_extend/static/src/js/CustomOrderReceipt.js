/** @odoo-module **/

import { Component } from "@odoo/owl";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { OrderWidget } from "@point_of_sale/app/generic_components/order_widget/order_widget";
import { ReceiptHeader } from "@point_of_sale/app/screens/receipt_screen/receipt/receipt_header/receipt_header";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { omit } from "@web/core/utils/objects";

export class CustomOrderReceipt extends OrderReceipt {
    static template = "pos_receipt_extend.CustomOrderReceipt";
    static components = {
        Orderline,
        OrderWidget,
        ReceiptHeader,
    };
    static props = {
        data: Object,
        formatCurrency: Function,
        basic_receipt: { type: Boolean, optional: true },
    };
    static defaultProps = {
        basic_receipt: false,
    };

    omit(...args) {
        return omit(...args);
    }

    doesAnyOrderlineHaveTaxLabel() {
        return this.props.data.orderlines.some((line) => line.taxGroupLabels);
    }
}