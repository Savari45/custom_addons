// pos_whatsapp/static/src/js/pos_whatsapp.js
odoo.define('pos_whatsapp.WhatsAppButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require("@web/core/utils/hooks");

    class WhatsAppButton extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }

        async onClick() {
            const order = this.env.pos.get_order();
            if (!order || !order.get_client()) {
                this.showPopup('ErrorPopup', {
                    title: this.env._t('No Customer'),
                    body: this.env._t('Please select a customer first.'),
                });
                return;
            }

            const client = order.get_client();
            const phone = client.phone ? client.phone.replace(/\D/g, '') : '';

            if (!phone) {
                this.showPopup('ErrorPopup', {
                    title: this.env._t('No Phone Number'),
                    body: this.env._t('Customer has no phone number set.'),
                });
                return;
            }

            const products = order.get_orderlines().map(line =>
                `- ${line.get_product().display_name} × ${line.get_quantity()} = ₹${line.get_price_with_tax()}`
            ).join('\n');

            const message =
                `${this.env._t('Hi')} ${client.name || this.env._t('Customer')},\n\n` +
                `🧾 *${this.env._t('Your Order Details')}:*\n` +
                `${products}\n\n` +
                `🧮 *${this.env._t('Total')}: ₹${order.get_total_with_tax()}*\n\n` +
                `${this.env._t('Thank you for shopping with us!')}`;

            const encodedMsg = encodeURIComponent(message);
            window.open(`https://wa.me/${phone}?text=${encodedMsg}`, '_blank');
        }
    }

    WhatsAppButton.template = 'WhatsAppButton';
    Registries.Component.add(WhatsAppButton);

    return WhatsAppButton;
});