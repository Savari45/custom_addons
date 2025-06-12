from odoo import models, fields,api
from datetime import timedelta, datetime
from datetime import timedelta

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Add new option to the selection field
    delivery_status = fields.Selection(
        selection_add=[('in_transit', 'In Transit')],
        compute='_compute_delivery_status',
        store=True
    )

    shopify_payment_status = fields.Selection([
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled')
    ], string="Shopify Payment Status")

    tracking_number = fields.Char(string="Tracking Number",readonly=False)
    delivery_partner = fields.Char(string="Delivery Partner")
    shopify_order_id = fields.Char(string="Shopify Order ID", readonly=False)


    commitment_date = fields.Datetime(string='Delivery Date')
    intransit_days = fields.Integer(string='Intransit Days', store=True)


    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        invoice_vals.update({
            'shopify_order_id': self.shopify_order_id,
            'tracking_number': self.tracking_number,
            'delivery_partner': self.delivery_partner,
        })
        return invoice_vals
    @api.model
    def action_mark_full_delivery(self):
        for order in self:
            order.delivery_status = 'full'
            order.commitment_date = fields.Datetime.now()

    def compute_intransit_days_cron(self):
        """Update intransit_days only if delivery_status is 'in_transit' and commitment_date is empty."""
        orders = self.search([
            ('commitment_date', '=', False),
            ('date_order', '!=', False),
            ('delivery_status', '=', 'in_transit'),
        ])
        now = datetime.now()
        for order in orders:
            delta = now - order.date_order
            order.intransit_days = delta.days



    # def compute_intransit_days_cron(self):
    #     """Update intransit_days in minutes if delivery_status is 'in_transit' and commitment_date is empty."""
    #     orders = self.search([
    #         ('commitment_date', '=', False),
    #         ('date_order', '!=', False),
    #         ('delivery_status', '=', 'in_transit'),
    #     ])
    #     now = datetime.now()
    #     for order in orders:
    #         delta = now - order.date_order
    #         order.intransit_days = int(delta.total_seconds() / 60)

    # @api.model
    # def update_intransit_days(self):
    #     orders = self.search([('date_order', '!=', False), ('commitment_date', '=', False)])
    #     for order in orders:
    #         order._compute_intransit_days()

    @api.depends('picking_ids', 'picking_ids.state')
    def _compute_delivery_status(self):
        for order in self:
            if not order.picking_ids or all(p.state == 'cancel' for p in order.picking_ids):
                order.delivery_status = False
            elif all(p.state in ['done', 'cancel'] for p in order.picking_ids):
                order.delivery_status = 'in_transit'
            elif any(p.state == 'done' for p in order.picking_ids) and any(
                    l.qty_delivered for l in order.order_line):
                order.delivery_status = 'partial'
            elif any(p.state == 'done' for p in order.picking_ids):
                order.delivery_status = 'started'
            else:
                order.delivery_status = 'pending'






