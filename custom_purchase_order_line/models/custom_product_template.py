from odoo import models, fields, api,_
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if self.env.context.get('from_purchase_order_line'):
                if vals.get('type') not in ['consu', 'service', 'combo']:
                    vals['type'] = 'consu'  # Default to 'consu' if invalid
                vals['is_storable'] = True  # Ensure 'is_storable' is set
        return super().create(vals_list)

    @api.model
    def name_create(self, name):
        """Intercept 'Create and Edit' and show the confirmation wizard before creating a product"""
        wizard = self.env['purchase.product.confirmation.wizard'].create({
            'new_product_name': name,
        })
        return wizard.action_open_wizard()


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if self.env.context.get('from_purchase_order_line'):
                if vals.get('type') not in ['consu', 'service', 'combo']:
                    vals['type'] = 'consu'  # Default to 'consu' if invalid
                vals['is_storable'] = True  # Ensure 'is_storable' is set
        return super().create(vals_list)

    @api.model
    def name_create(self, name):
        """Intercept 'Create and Edit' and open the confirmation wizard"""
        wizard = self.env['purchase.product.confirmation.wizard'].create({
            'new_product_name': name,
        })
        return wizard.action_open_wizard()


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    allow_direct_creation = fields.Boolean(default=True)

    @api.model_create_multi
    def create(self, vals):
        if vals.get('product_id') and not self.env['product.product'].browse(vals['product_id']).exists():
            raise UserError(_("Do you want to create this product?"))
        return super(PurchaseOrderLine, self).create(vals)