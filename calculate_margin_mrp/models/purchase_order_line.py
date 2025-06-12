from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    mrp = fields.Float(string='MRP', help="You can enter MRP manually or let it auto-calculate based on margin %.",readonly=False)
    margin_percentage = fields.Float(string='Margin %', help="Enter margin % to auto-fill MRP, or vice versa.",readonly=False)

    @api.onchange('mrp', 'price_unit')
    def _onchange_mrp_or_price(self):
        for line in self:
            price_with_tax = line.price_unit
            if line.taxes_id:
                taxes = line.taxes_id.compute_all(
                    line.price_unit,
                    line.order_id.currency_id,
                    quantity=1.0,
                    product=line.product_id,
                    partner=line.order_id.partner_id,
                )
                price_with_tax = taxes.get('total_included', line.price_unit)

            if price_with_tax > 0 and line.mrp:
                line.margin_percentage = round(
                    ((line.mrp - price_with_tax) / price_with_tax) * 100, 2
                )
            elif not line.mrp:
                # Optional: Set a default MRP if nothing entered
                line.mrp = round(price_with_tax * 2, 2)
                line.margin_percentage = 100.0

    @api.onchange('margin_percentage')
    def _onchange_margin(self):
        for line in self:
            price_with_tax = line.price_unit
            if line.taxes_id:
                taxes = line.taxes_id.compute_all(
                    line.price_unit,
                    line.order_id.currency_id,
                    quantity=1.0,
                    product=line.product_id,
                    partner=line.order_id.partner_id,
                )
                price_with_tax = taxes.get('total_included', line.price_unit)

            if price_with_tax > 0 and line.margin_percentage:
                line.mrp = round(
                    price_with_tax * (1 + (line.margin_percentage / 100)), 2
                )
