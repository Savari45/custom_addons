from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression
import re
import logging
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_id = fields.Many2one(
        'product.product',
        domain="[('product_id.qty_available', '>', 0)]",  # Ensures only positive stock products
        required=True
    )
    product_template_id = fields.Many2one(
        'product.template',
        domain="[('qty_available', '>', 0)]",  # Ensures only positive stock products
        required=True
    )

    @api.constrains('product_id')
    def _check_product_stock(self):
        for line in self:
            if line.product_id.qty_available <= 0:
                raise ValidationError(f"The product {line.product_id.name} is out of stock!")

class ResPartner(models.Model):
   _inherit = 'res.partner'
   adhar_no = fields.Char(string="Adhar Number",size=12)
   @api.model
   def name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
       domain = expression.AND([[('mobile', operator, name)], args or []])
       records = self.search_fetch(domain, ['mobile'], limit=limit)
       return [(record.id, record.display_name) for record in records.sudo()]

   @api.constrains('adhar_no')  # Ensure correct field name
   def _check_aadhar_number(self):
       for record in self:
           if record.adhar_no and not re.fullmatch(r'\d{12}', record.adhar_no):
               raise ValidationError(_("Aadhar Number must be exactly 12 digits and contain only numbers."))

class SaleOrder(models.Model):
    _inherit = 'sale.order'


    mobile = fields.Char(related='partner_id.mobile', string='Mobile Number', readonly=True, store=True)
    adhar = fields.Char(related='partner_id.adhar_no',string="Adhar Number", store=True,copy=True)


    def action_print_invoice(self):
        """Finds the invoice linked to the sale order and calls the print function."""
        self.ensure_one()  # Ensure a single record is processed

        invoice = self.invoice_ids.filtered(lambda inv: inv.state in ['posted', 'draft'])

        if not invoice:
            raise UserError(
                "No invoice found for this Sale Order! Please ensure the invoice is created and in Draft or Posted state.")

        # Get the print report function from `account.move`
        return self.env.ref('custom_sale_purchase.action_report_pos_invoice').report_action(invoice)
    def action_a4_print_invoice(self):
        """Finds the invoice linked to the sale order and calls the print function."""
        self.ensure_one()  # Ensure a single record is processed

        invoice = self.invoice_ids.filtered(lambda inv: inv.state in ['posted', 'draft'])

        if not invoice:
            raise UserError(
                "No invoice found for this Sale Order! Please ensure the invoice is created and in Draft or Posted state.")

        # Get the print report function from `account.move`
        return self.env.ref('account.account_invoices').report_action(invoice)






class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"


    price_unit = fields.Float(string ="Unit price",compute='_compute_unit_price', store=True)
    price_subtotal = fields.Monetary(
        string="Subtotal",
        store=True,
        readonly=False                # Allow manual entry
    )


    @api.depends('product_qty','price_subtotal')
    def _compute_unit_price(self):
        print("welcome")
        """When the user changes price_subtotal, auto-update price_unit."""
        for line in self:
            if line.product_qty > 0:
                line.price_unit = line.price_subtotal / line.product_qty

