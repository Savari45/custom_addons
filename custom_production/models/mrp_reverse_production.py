from odoo import models, api, _
from odoo.exceptions import UserError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def action_reverse_production(self):
        for order in self:
            if order.state != 'done':
                raise UserError(_("Only completed orders can be reversed."))

            # Reverse finished goods
            for move in order.move_finished_ids:
                if move.state == 'done':
                    reverse_move = move.copy({
                        'location_id': move.location_dest_id.id,
                        'location_dest_id': move.location_id.id,
                        'origin_returned_move_id': move.id,
                        'move_orig_ids': [],
                        'move_dest_ids': [],
                    })
                    reverse_move._action_confirm()
                    for line in move.move_line_ids:
                        reverse_line = reverse_move.move_line_ids.filtered(lambda l: l.product_id == line.product_id)
                        reverse_line.write({'qty_done': line.qty_done})
                    reverse_move._action_done()

            # Reverse raw materials
            for move in order.move_raw_ids:
                if move.state == 'done':
                    reverse_move = move.copy({
                        'location_id': move.location_dest_id.id,
                        'location_dest_id': move.location_id.id,
                        'origin_returned_move_id': move.id,
                        'move_orig_ids': [],
                        'move_dest_ids': [],
                    })
                    reverse_move._action_confirm()
                    for line in move.move_line_ids:
                        reverse_line = reverse_move.move_line_ids.filtered(lambda l: l.product_id == line.product_id)
                        reverse_line.write({'qty_done': line.qty_done})
                    reverse_move._action_done()

            # Reset MO state and flags
            order.write({
                'state': 'progress',
                'is_initial_produced': False,
                'is_validated': False,
            })

            # ✂️ Example: Delete a component
            component_to_delete = order.move_raw_ids.filtered(
                lambda m: m.product_id.default_code == 'OLD-COMP'
            )
            component_to_delete.unlink()

            # 🔁 Example: Modify component quantity
            component_to_modify = order.move_raw_ids.filtered(
                lambda m: m.product_id.default_code == 'NEW-COMP'
            )
            for move in component_to_modify:
                move.product_uom_qty = 10.0  # New desired quantity

            # Optional: Recreate or adjust moves if needed
            # order._create_moves()
