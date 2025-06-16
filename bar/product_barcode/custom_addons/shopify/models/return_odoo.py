from odoo import models, fields, api
import requests
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

class ShopifySaleSync(models.Model):
    _name = 'shopify.sale.sync'
    _description = 'Sync Shopify Returns/Refunds/Exchanges with Odoo'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def poll_shopify_and_sync_refunds(self):
        instance = self.env['shopify.instance'].search([], limit=1)
        if not instance:
            _logger.error("No Shopify instance found.")
            return

        shopify_domain = instance.shopify_domain
        access_token = instance.shopify_token
        headers = {
            'X-Shopify-Access-Token': access_token,
            'Content-Type': 'application/json',
        }

        url = f"https://{shopify_domain}/admin/api/2025-04/orders.json?status=any&limit=50"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        orders = response.json().get('orders', [])

        for order in orders:
            shopify_order_id = str(order.get('id'))
            odoo_order = self.env['sale.order'].search([('shopify_order_id', '=', shopify_order_id)], limit=1)
            if not odoo_order:
                continue

            # --- Process Returns & Exchanges ---
            # Shopify API: returns can contain both returned and exchanged items
            if order.get('returns'):
                for return_data in order['returns']:
                    self._handle_return(odoo_order, return_data)
                    self._handle_exchange(odoo_order, return_data)

            # --- Process Refunds ---
            if order.get('refunds'):
                for refund in order['refunds']:
                    self._handle_refund(odoo_order, refund)

    def _handle_refund(self, odoo_order, refund):
        already_refunded = odoo_order.invoice_ids.filtered(
            lambda i: i.move_type == 'out_refund' and i.state == 'posted'
        )
        if already_refunded:
            _logger.info(f"Order {odoo_order.name} already refunded.")
            return

        for invoice in odoo_order.invoice_ids.filtered(lambda i: i.state == 'posted' and i.move_type == 'out_invoice'):
            refund_wizard = self.env['account.move.reversal'].with_context(
                active_model='account.move', active_ids=invoice.ids
            ).create({
                'reason': 'Shopify refund',
                'date': fields.Date.today(),
                'journal_id': invoice.journal_id.id,
            })
            refund_wizard.reverse_moves()
            _logger.info(f"Refunded invoice {invoice.name} for Shopify order {odoo_order.name}")

        for refund_line in refund.get('refund_line_items', []):
            shopify_line_id = refund_line.get('line_item_id')
            qty = refund_line.get('quantity', 0)
            so_line = odoo_order.order_line.filtered(lambda l: l.shopify_line_id == shopify_line_id)
            for l in so_line:
                l.write({'name': l.name + f" (Returned x{qty})"})

    def _handle_return(self, odoo_order, return_data):
        picking = odoo_order.picking_ids.filtered(
            lambda p: p.state == 'done' and p.picking_type_code == 'outgoing'
        )
        if not picking:
            _logger.warning(f"No done delivery to return for order {odoo_order.name}")
            return

        ReturnPicking = self.env['stock.return.picking'].with_context(
            active_id=picking.id, active_ids=[picking.id]
        )

        product_returns = []
        for return_line in return_data.get('return_line_items', []):
            shopify_line_id = return_line.get('line_item_id')
            qty = return_line.get('quantity', 0)
            so_line = odoo_order.order_line.filtered(lambda l: l.shopify_line_id == shopify_line_id)
            move = picking.move_ids.filtered(lambda m: m.product_id == so_line.product_id)
            if so_line and move:
                product_returns.append((0, 0, {
                    'product_id': so_line.product_id.id,
                    'quantity': qty,
                    'move_id': move.id,
                }))

        if product_returns:
            return_wizard = ReturnPicking.create({
                'product_return_moves': product_returns,
            })
            return_wizard.create_returns()
            _logger.info(f"Stock return created for Shopify order {odoo_order.name}")

    def _handle_exchange(self, odoo_order, return_data):
        # Check if there are exchange_line_items (Shopify: items sent as exchange)
        exchange_lines = return_data.get('exchange_line_items', [])
        if not exchange_lines:
            return

        for exch in exchange_lines:
            sku = exch.get('sku') or ''
            quantity = exch.get('quantity', 0)
            price = float(exch.get('price', 0.0))
            title = exch.get('title') or sku
            # Find product in Odoo
            product = self.env['product.product'].search([('default_code', '=', sku)], limit=1)
            if not product:
                # Create the product if not exist
                product = self.env['product.product'].create({
                    'name': title,
                    'default_code': sku,
                    'list_price': price,
                })

            # Create a new sale order line (could also create a new order if preferred)
            self.env['sale.order.line'].create({
                'order_id': odoo_order.id,
                'product_id': product.id,
                'product_uom_qty': quantity,
                'price_unit': price,
                'name': title + " (Exchange)",
            })
            _logger.info(f"Added exchanged item '{title}' x{quantity} to order {odoo_order.name}")
