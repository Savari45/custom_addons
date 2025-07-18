from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    location_dest_id = fields.Many2one(
        'stock.location',
        string="Destination Location",

    )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        picking_type_id = res.get('picking_type_id')
        if picking_type_id:
            picking_type = self.env['stock.picking.type'].browse(picking_type_id)
            if picking_type.code == 'internal':
                transit_location = self.env['stock.location'].search([
                    ('usage', '=', 'transit')
                ], limit=1)
                if transit_location:
                    res['location_dest_id'] = transit_location.id
        return res

