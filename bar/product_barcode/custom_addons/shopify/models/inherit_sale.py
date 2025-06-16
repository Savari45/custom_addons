from odoo import models, fields, api
import requests
from datetime import datetime

from odoo.exceptions import UserError


class ShopifyOrderUpdate(models.Model):
    _name = 'shopify.order.update'
    _description = 'Shopify Order Update'

    name = fields.Char("Order Update Job")

    @api.model
    def sync_shopify_orders(self):
        # Shopify API credentials
        shopify_domain = "development-avant-garde.myshopify.com"
        access_token = "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"

        # Shopify API endpoint to get orders updates (edit or return)
        url = f"https://{shopify_domain}/admin/api/2024-01/orders.json?status=any"

        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": access_token
        }

        # Send the GET request to Shopify API
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise UserError(
                f"Failed to fetch orders from Shopify. Status Code: {response.status_code} - {response.text}")

        # Process Shopify orders
        orders = response.json().get('orders', [])

        for order in orders:
            shopify_order_id = str(order.get('id'))
            # Find the corresponding Sale Order in Odoo
            sale_order = self.env['sale.order'].search([('shopify_order_id', '=', shopify_order_id)], limit=1)

            if sale_order:
                # Update the Sale Order based on Shopify order update
                self._update_sale_order_from_shopify(sale_order, order)

    def _update_sale_order_from_shopify(self, sale_order, shopify_order):
        """Helper method to update Sale Order with Shopify order details"""

        # Check for line item updates
        for line_item in shopify_order.get('line_items', []):
            shopify_line_id = line_item.get('id')
            # Find the corresponding sale order line based on Shopify line ID
            order_line = sale_order.order_line.filtered(lambda l: l.shopify_line_id == shopify_line_id)

            if order_line:
                # Update the order line (e.g., product change, quantity)
                order_line.product_uom_qty = line_item.get('quantity')

        # Handle return or refund case: Create a return or credit note if necessary
        if shopify_order.get('refunds'):
            for refund in shopify_order['refunds']:
                # Handle creating a refund/credit note in Odoo
                self._create_credit_note_for_return(sale_order, refund)

    def _create_credit_note_for_return(self, sale_order, refund_data):
        """Helper method to create a credit note for a return"""
        # Example: Creating a credit note based on Shopify refund details
        credit_note = self.env['account.move'].create({
            'move_type': 'out_refund',  # Creating a refund
            'partner_id': sale_order.partner_id.id,
            'invoice_origin': sale_order.name,
            'ref': refund_data.get('id'),
            'invoice_line_ids': [(0, 0, {
                'product_id': sale_order.order_line[0].product_id.id,
                'quantity': refund_data.get('total_taxable', 0),
                'price_unit': sale_order.order_line[0].price_unit,
            })],
        })
        credit_note.action_post()  # Post the credit note
