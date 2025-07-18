from odoo import models, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_all_product_transfer(self):
        for picking in self:
            if picking.state not in ['draft', 'confirmed', 'assigned']:
                raise UserError(_("Only draft or ready transfers can be used for this action."))

            source_location = picking.location_id

            # Get all quant records for source location with qty > 0
            quants = self.env['stock.quant'].sudo().search([
                ('location_id', '=', source_location.id),
                ('quantity', '>', 0),
            ])

            if not quants:
                raise UserError(_("No products with available quantity in source location: %s") % source_location.display_name)

            move_commands = []
            picking.move_ids = False
            for quant in quants:
                product = quant.product_id
                cost = product.product_tmpl_id.standard_price
                print(f"Product: {product.name}, Standard Price: {cost}")

                move_commands.append((0, 0, {
                    'product_id': product.id,
                    'product_uom_qty': quant.quantity,
                    'product_uom': product.uom_id.id,
                    'name': product.display_name,
                    'location_id': source_location.id,
                    'location_dest_id': picking.location_dest_id.id,
                    'company_id': picking.company_id.id,
                    # Optional: Store cost temporarily in a custom field if you want
                    # 'cost_price': cost,  # You need to add this custom field in stock.move
                }))

            picking.move_ids = move_commands
