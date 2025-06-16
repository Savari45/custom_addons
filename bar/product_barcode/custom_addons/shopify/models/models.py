import requests
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.template'
    shopify_inventory_item_id = fields.Char("Shopify Inventory Item ID")


class ShopifyOrderImport(models.Model):
    _name = 'shopify.order.import'
    _description = 'Shopify Order Import'
    _order = 'name desc'

    name = fields.Char(string="Order Name")
    shopify_order_id = fields.Char(string="Shopify Order ID")
    total_amount = fields.Float(string="Total Amount")
    customer_name = fields.Char(string="Customer Name")
    payment_status = fields.Char(string="Payment Status")
    fulfillment_status = fields.Char(string="Fulfillment Status")
    last_import_date = fields.Datetime(string="Last Import Date", default=lambda self: datetime.now())
    tracking = fields.Char(string='Tracking Number')
    courier = fields.Char(string='Delivery Partner')

    @api.model
    def import_shopify_orders(self, *args, **kwargs):
        instance = self.env['shopify.instance'].search([], limit=1)
        if not instance:
            raise ValueError("No Shopify instance found")

        shopify_domain = instance.shopify_domain
        access_token = instance.shopify_token

        base_url = f"https://{shopify_domain}/admin/api/2024-01/orders.json"
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": access_token,
        }

        latest_import = self.env['shopify.order.import'].search([], limit=1)
        last_import_date = latest_import.last_import_date if latest_import else None

        if last_import_date:
            since_date = (last_import_date - timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S")
            url = f"{base_url}?updated_at_min={since_date}&status=any"
        else:
            url = f"{base_url}?status=any"

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise UserError(f"Failed to fetch orders from Shopify! Status Code: {response.status_code} - Response: {response.text}")

        orders = response.json().get('orders', [])
        _logger.info(f"Fetched {len(orders)} orders from Shopify.")

        for order in orders:
            shopify_order_id = str(order.get('id'))
            existing_order = self.env['shopify.order.import'].search([('shopify_order_id', '=', shopify_order_id)], limit=1)
            existing_sale = self.env['sale.order'].search([('shopify_order_id', '=', shopify_order_id)], limit=1)

            customer_name = ""
            if order.get('customer'):
                customer_name = f"{order['customer'].get('first_name', '')} {order['customer'].get('last_name', '')}".strip()

            payment_status = order.get('financial_status') or 'unknown'
            fulfillment_status = order.get('fulfillment_status') or ''
            fulfillments = order.get('fulfillments', [])

            if not fulfillment_status and fulfillments and fulfillments[0].get('status'):
                fulfillment_status = fulfillments[0]['status']
            elif not fulfillment_status:
                fulfillment_status = 'unfulfilled'

            tracking_number = ""
            courier_name = ""

            for fulfillment in reversed(fulfillments):
                if fulfillment.get('status') != 'cancelled':
                    tracking_number = fulfillment.get('tracking_number', '') or ''
                    courier_name = fulfillment.get('tracking_company', '') or ''
                    break

            vals = {
                'name': order.get('name', ''),
                'shopify_order_id': shopify_order_id,
                'total_amount': float(order.get('total_price', 0.0)),
                'customer_name': customer_name,
                'payment_status': payment_status,
                'fulfillment_status': fulfillment_status,
                'last_import_date': datetime.now(),
                'tracking': tracking_number,
                'courier': courier_name,
            }

            _logger.info(f"Processing Shopify Order {order.get('name')} - Payment: {payment_status}, Fulfillment: {fulfillment_status}")

            if existing_order:
                existing_order.write(vals)
            else:
                self.env['shopify.order.import'].create(vals)

            if existing_sale:
                updates_needed = {}

                if fulfillment_status == 'cancelled':
                    updates_needed['tracking_number'] = ''
                    updates_needed['delivery_partner'] = ''
                else:
                    if existing_sale.tracking_number != tracking_number:
                        updates_needed['tracking_number'] = tracking_number
                    if existing_sale.delivery_partner != courier_name:
                        updates_needed['delivery_partner'] = courier_name

                if existing_sale.amount_total != float(order.get('total_price', 0.0)):
                    updates_needed['amount_total'] = float(order.get('total_price', 0.0))

                if existing_sale.state != 'sale' and fulfillment_status == 'fulfilled':
                    updates_needed['state'] = 'sale'

                if updates_needed:
                    existing_sale.write(updates_needed)
                    _logger.info(f"Updated Sale Order {existing_sale.name} with changes: {updates_needed}")

                existing_lines = {line.product_id.default_code: line for line in existing_sale.order_line}
                incoming_skus = set()

                for line in order.get('line_items', []):
                    sku = line.get('sku')
                    quantity = float(line.get('quantity', 1))
                    price_unit = float(line.get('price', 0.0))
                    incoming_skus.add(sku)

                    product = self.env['product.product'].search([('default_code', '=', sku)], limit=1)
                    if not product:
                        _logger.warning(f"Product with SKU '{sku}' not found.")
                        continue

                    line_vals = {
                        'product_id': product.id,
                        'product_uom_qty': quantity,
                        'price_unit': price_unit,
                        'order_id': existing_sale.id,
                    }

                    if sku in existing_lines:
                        existing_lines[sku].write(line_vals)
                    else:
                        self.env['sale.order.line'].create(line_vals)

                # Remove obsolete lines
                for sku, line in existing_lines.items():
                    if sku not in incoming_skus:
                        line.unlink()
                        _logger.info(f"Removed obsolete line for SKU: {sku} from Sale Order: {existing_sale.name}")

                _logger.info(f"Updated Sale Order {existing_sale.name} for Shopify Order ID: {shopify_order_id}")
            else:
                _logger.info(f"No existing Sale Order found for Shopify Order ID: {shopify_order_id}, skipping creation.")
