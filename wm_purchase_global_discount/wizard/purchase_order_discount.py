# -*- coding: utf-8 -*-
# Copyright 2020 CorTex IT Solutions Ltd. (<https://cortexsolutions.net/>)
# License OPL-1

from odoo import Command, _, api, fields, models
from odoo.exceptions import ValidationError


class PurchaseOrderDiscount(models.TransientModel):
    _name = 'purchase.order.discount'
    _description = "Purchase Order Discount Wizard"

    purchase_order_id = fields.Many2one(
        'purchase.order', default=lambda self: self.env.context.get('active_id'), required=True)
    company_id = fields.Many2one(related='purchase_order_id.company_id', store=True)
    currency_id = fields.Many2one(related='purchase_order_id.currency_id', store=True)
    discount_amount = fields.Monetary(string="Discount Amount", required=True)

    @api.constrains('discount_amount')
    def _check_discount_amount(self):
        """Ensure discount amount is valid"""
        for wizard in self:
            if wizard.discount_amount <= 0:
                raise ValidationError(_("Discount amount must be greater than zero."))

    def _get_or_create_discount_product(self):
        """Retrieve or create a discount product"""
        self.ensure_one()
        discount_product = self.company_id.purchase_discount_product_id
        if not discount_product:
            discount_product = self.env['product.product'].create({
                'name': _('Purchase Discount'),
                'type': 'service',
                'purchase_method': 'purchase',
                'list_price': 0.0,
                'company_id': self.company_id.id,
                'taxes_id': [Command.clear()],
            })
            self.company_id.purchase_discount_product_id = discount_product
        return discount_product

    def action_apply_discount(self):
        """Apply the discount to the Purchase Order"""
        self.ensure_one()
        discount_product = self._get_or_create_discount_product()

        # Instead of removing old discounts, we now allow multiple discounts
        self.env['purchase.order.line'].create({
            'order_id': self.purchase_order_id.id,
            'product_id': discount_product.id,
            'name': _('Discount (₹{})'.format(self.discount_amount)),
            'sequence': 999,
            'price_unit': -self.discount_amount,  # Negative for discount effect
            'taxes_id': [Command.clear()],  # No taxes on discounts
        })
