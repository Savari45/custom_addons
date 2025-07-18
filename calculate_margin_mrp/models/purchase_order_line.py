from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    mrp = fields.Float(string='MRP', help="Manually enter or auto-compute based on margin %.")
    margin_percentage = fields.Float(string='Margin %', help="Used to auto-compute MRP.")
    discount = fields.Float(string='Discount (%)')  # Add this field if not already inherited

    @api.onchange('mrp', 'price_unit', 'discount', 'taxes_id')
    def _onchange_mrp_or_price(self):
        for line in self:
            price_after_discount = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            price_with_tax = price_after_discount

            if line.taxes_id:
                taxes = line.taxes_id.compute_all(
                    price_after_discount,
                    line.order_id.currency_id,
                    quantity=1.0,
                    product=line.product_id,
                    partner=line.order_id.partner_id,
                )
                price_with_tax = taxes.get('total_included', price_after_discount)

            if price_with_tax > 0 and line.mrp:
                line.margin_percentage = round(
                    ((line.mrp - price_with_tax) / price_with_tax) * 100, 2
                )
            elif not line.mrp:
                line.mrp = round(price_with_tax * 2, 2)
                line.margin_percentage = 100.0

    @api.onchange('margin_percentage', 'discount', 'taxes_id')
    def _onchange_margin(self):
        for line in self:
            price_after_discount = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            price_with_tax = price_after_discount

            if line.taxes_id:
                taxes = line.taxes_id.compute_all(
                    price_after_discount,
                    line.order_id.currency_id,
                    quantity=1.0,
                    product=line.product_id,
                    partner=line.order_id.partner_id,
                )
                price_with_tax = taxes.get('total_included', price_after_discount)

            if price_with_tax > 0 and line.margin_percentage:
                line.mrp = round(
                    price_with_tax * (1 + (line.margin_percentage / 100)), 2
                )
