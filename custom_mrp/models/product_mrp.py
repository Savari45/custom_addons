from odoo import fields,models, api

class ProductTemplate(models.Model):
    _inherit = "product.template"

    mrp_price = fields.Float(string="MRP")


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    mrp_price = fields.Float(
        related="product_template_id.mrp_price",
        string="MRP",
        readonly=False
    )
    price_difference_per_unit = fields.Float(
        string="Difference per Unit (MRP - Sale Price)",
        compute="_compute_price_difference",
        store=True
    )
    total_difference = fields.Float(
        string="Total Difference",
        compute="_compute_total_difference",
        store=True
    )

    @api.depends('mrp_price', 'price_unit')
    def _compute_price_difference(self):
        for line in self:
            line.price_difference_per_unit = line.mrp_price - line.price_unit


    @api.depends('price_difference_per_unit', 'product_uom_qty')
    def _compute_total_difference(self):
        for line in self:
            line.total_difference = line.price_difference_per_unit * line.product_uom_qty


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'total_difference': self._get_total_difference(),
            'difference_percentage': self._get_difference_percentage(),
        })
        return invoice_vals

    def _get_total_difference(self):
        total_difference = 0.0
        for line in self.order_line:
            line_difference = (line.mrp_price - line.price_unit) * line.product_uom_qty
            total_difference += line_difference
        return total_difference

    def _get_difference_percentage(self):
        total_mrp = sum(line.mrp_price * line.product_uom_qty for line in self.order_line)
        total_sale = sum(line.price_unit * line.product_uom_qty for line in self.order_line)
        if total_mrp:
            return ((total_mrp - total_sale) / total_mrp) * 100
        return 0.0
class AccountMove(models.Model):
    _inherit = 'account.move'

    total_difference = fields.Float(string="Total Difference")
    difference_percentage = fields.Float(string="Difference Percentage")