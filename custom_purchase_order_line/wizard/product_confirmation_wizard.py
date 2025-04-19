from odoo import models, fields, api

class ProductConfirmationWizard(models.TransientModel):
    _name = 'purchase.product.confirmation.wizard'
    _description = 'Product Confirmation Wizard'

    new_product_name = fields.Char(string="New Product Name", readonly=True)
    message = fields.Char(default="Do you want to create this product?")

    def action_create_product(self):
        """Create the product and open the form"""
        product = self.env['product.product'].create({
            'name': self.new_product_name,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Product',
            'res_model': 'product.product',
            'res_id': product.id,
            'view_mode': 'form',
            'target': 'current',  # Open the created product form
        }

    def action_cancel(self):
        """Close wizard and return to purchase order line"""
        return {'type': 'ir.actions.act_window_close'}

    def action_open_wizard(self):
        """Return action to open the wizard as a popup"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Confirm Product Creation',
            'res_model': 'purchase.product.confirmation.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',  # Open as a popup
        }
