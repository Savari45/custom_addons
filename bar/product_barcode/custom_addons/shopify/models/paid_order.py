from odoo import models, fields
import requests
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = 'product.product'
    shopify_product_id = fields.Char("Shopify Product ID", index=True)


class AccountMove(models.Model):
    _inherit = 'account.move'

    shopify_order_id = fields.Char("Shopify Order ID")
    tracking_number = fields.Char(string="Tracking Number")
    delivery_partner = fields.Char(string="Delivery Partner")


class SaleOrders(models.Model):
    _inherit = 'sale.order'

    _order = 'origin desc'

    shopify_order_id = fields.Char(string="Shopify Order ID", index=True)
    tracking_number = fields.Char(string="Tracking Number")
    delivery_partner = fields.Char(string="Delivery Partner")
    shopify_payment_status = fields.Char(string="Shopify Payment Status")


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    shopify_line_id = fields.Char(string="Shopify Line Item ID", index=True)
    is_returned = fields.Boolean("Returned (Shopify)")
    returned_qty = fields.Float("Returned Qty")


class ShopifySaleImport(models.Model):
    _name = 'shopify.sale.paid.order'
    _description = 'Import Shopify Paid/Partially Paid Orders into Odoo'

    def import_paid_shopify_sale_orders(self):
        instance = self.env['shopify.instance'].search([], limit=1)
        if not instance:
            _logger.error("❌ No Shopify instance found in the system.")
            return

        shopify_domain = instance.shopify_domain
        access_token = instance.shopify_token

        url = f"https://{shopify_domain}/admin/api/2023-04/orders.json"
        headers = {
            'X-Shopify-Access-Token': access_token,
            'Content-Type': 'application/json',
        }

        params = {
            'financial_status': 'paid,partially_paid,unpaid',
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
        except Exception as e:
            _logger.error(f"Error fetching Shopify Paid Orders: {e}")
            return

        orders_data = response.json().get('orders', [])
        _logger.info(f"📦 Fetched {len(orders_data)} paid/partially_paid orders from Shopify.")

        for order in orders_data:
            shopify_id = order.get('id')
            origin = f"Shopify-{shopify_id}"
            payment_status = order.get('financial_status', 'pending')

            fulfillments = order.get('fulfillments', [])
            tracking_number = ""
            delivery_partner = ""
            if fulfillments:
                latest_fulfillment = sorted(fulfillments, key=lambda f: f.get('created_at', ''), reverse=True)[0]
                tracking_number = latest_fulfillment.get('tracking_number', '')
                delivery_partner = latest_fulfillment.get('tracking_company', '')

            existing_order = self.env['sale.order'].search([('origin', '=', origin)], limit=1)

            if existing_order:
                vals_to_update = {}
                if existing_order.tracking_number != tracking_number:
                    vals_to_update['tracking_number'] = tracking_number
                if existing_order.delivery_partner != delivery_partner:
                    vals_to_update['delivery_partner'] = delivery_partner
                if existing_order.shopify_payment_status != payment_status:
                    vals_to_update['shopify_payment_status'] = payment_status

                if vals_to_update:
                    existing_order.write(vals_to_update)
                    _logger.info(f"✅ Updated info for order {existing_order.name}")

                for line in order.get('line_items', []):
                    sku = line.get('sku')
                    product = self.env['product.product'].search([('default_code', '=', sku)], limit=1)
                    if not product:
                        continue

                    order_lines = existing_order.order_line.filtered(lambda l: l.product_id.id == product.id)
                    updated_vals = self._prepare_order_line(line)

                    if order_lines:
                        for ol in order_lines:
                            need_update = (
                                    ol.product_uom_qty != updated_vals['product_uom_qty'] or
                                    ol.price_unit != updated_vals['price_unit'] or
                                    ol.shopify_line_id != updated_vals['shopify_line_id']
                            )
                            if need_update:
                                ol.write({
                                    'product_uom_qty': updated_vals['product_uom_qty'],
                                    'price_unit': updated_vals['price_unit'],
                                    'shopify_line_id': updated_vals['shopify_line_id'],
                                })
                                _logger.info(
                                    f"🔁 Updated product {line.get('title')} in existing order {existing_order.name}")
                    else:
                        updated_vals['order_id'] = existing_order.id
                        self.env['sale.order.line'].create(updated_vals)
                        _logger.info(f"➕ Added new product {line.get('title')} to existing order {existing_order.name}")

                continue

            partner_id = self._get_or_create_customer(order)
            if not partner_id:
                _logger.warning(f"Skipping order {shopify_id} - No valid customer.")
                continue

            created_at = order.get('created_at')
            formatted_created_at = fields.Datetime.now()
            if created_at:
                try:
                    created_at_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    formatted_created_at = created_at_dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass

            sale_order = self.env['sale.order'].create({
                'partner_id': partner_id,
                'origin': origin,
                'shopify_order_id': str(shopify_id),
                'name': order.get('name', ''),
                'date_order': formatted_created_at,
                'tracking_number': tracking_number,
                'delivery_partner': delivery_partner,
                'shopify_payment_status': payment_status,
                'order_line': [(0, 0, self._prepare_order_line(line)) for line in order.get('line_items', [])],
            })

            sale_order.action_confirm()
            _logger.info(f"🆕 Created and confirmed Sale Order: {sale_order.name} with status: {payment_status}")

    def _get_or_create_customer(self, order):
        customer = order.get('customer')
        if not customer:
            return False

        email = customer.get('email')
        name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip()
        phone = customer.get('phone') or ''
        default_address = customer.get('default_address', {})
        street = default_address.get('address1') or ''
        street2 = default_address.get('address2') or ''
        city = default_address.get('city') or ''
        zip_code = default_address.get('zip') or ''
        state_name = default_address.get('province') or ''
        country_name = default_address.get('country') or ''

        country_id = self.env['res.country'].search([('name', '=', country_name)], limit=1).id
        state_id = self.env['res.country.state'].search(
            [('name', '=', state_name), ('country_id', '=', country_id)],
            limit=1
        ).id

        if not email:
            return False

        partner = self.env['res.partner'].search([('email', '=', email)], limit=1)
        if not partner:
            partner = self.env['res.partner'].create({
                'name': name or 'Shopify Customer',
                'email': email,
                'phone': phone,
                'street': street,
                'street2': street2,
                'city': city,
                'zip': zip_code,
                'state_id': state_id,
                'country_id': country_id,
            })
            _logger.info(f"👤 Created new customer: {partner.name}")
        return partner.id

    def _prepare_order_line(self, line):
        product = self.env['product.product'].search([('default_code', '=', line.get('sku'))], limit=1)
        if not product:
            product = self.env['product.product'].create({
                'name': line.get('title'),
                'default_code': line.get('sku') or '',
                'list_price': float(line.get('price', 0.0)),
            })
            _logger.info(f"📦 Created new product: {product.name}")

        # ---- SHOPIFY LINE ID MAPPING ----
        shopify_line_id = ''
        line_item_id = line.get('id')
        if line_item_id:
            shopify_line_id = str(line_item_id)
        else:
            # Try some other keys as fallback (just in case)
            shopify_line_id = str(line.get('variant_id') or line.get('sku') or line.get('title') or 'NO_ID')
            _logger.warning(f"⚠️ No 'id' in line: {line}. Using fallback shopify_line_id={shopify_line_id}")

        # ---- LOG WHAT YOU ARE SAVING ----
        _logger.info(
            f"Saving order line: title='{line.get('title')}', sku='{line.get('sku')}', shopify_line_id='{shopify_line_id}'")

        tax_lines = line.get('tax_lines', [])
        tax_amount = sum(float(t.get('price', 0.0)) for t in tax_lines)

        quantity = float(line.get('quantity', 1))
        price = float(line.get('price', 0.0))
        unit_price_incl_tax = (price * quantity + tax_amount) / quantity if quantity else price

        return {
            'product_id': product.id,
            'product_uom_qty': quantity,
            'price_unit': unit_price_incl_tax,
            'name': line.get('title'),
            'shopify_line_id': shopify_line_id,
        }
