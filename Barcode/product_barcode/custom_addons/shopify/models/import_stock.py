from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    shopify_variant_id = fields.Char("Shopify Variant ID")
    shopify_inventory_item_id = fields.Char("Shopify Inventory Item ID")

    def action_import_shopify_stock(self):
        """Manual action to sync stock from Shopify and update via stock.quant"""
        instance = self.env['shopify.instance'].search([], limit=1)
        if not instance:
            raise UserError("❌ No Shopify instance configured.")

        shopify_domain = instance.shopify_domain
        access_token = instance.shopify_token

        headers = {
            'X-Shopify-Access-Token': access_token,
            'Content-Type': 'application/json',
        }

        location = self.env.ref('stock.stock_location_stock')  # Default internal location

        for product in self:
            inventory_item_id = product.shopify_inventory_item_id
            if not inventory_item_id:
                _logger.warning(f"⚠️ No inventory_item_id for '{product.name}' (ID {product.id})")
                continue

            stock_url = f"https://{shopify_domain}/admin/api/2023-04/inventory_levels.json?inventory_item_ids={inventory_item_id}"
            response = requests.get(stock_url, headers=headers)
            if response.status_code != 200:
                _logger.warning(f"❌ Failed to fetch stock for '{product.name}': {response.text}")
                continue

            inventory_levels = response.json().get("inventory_levels", [])
            if not inventory_levels:
                _logger.warning(f"⚠️ No stock data found for '{product.name}'")
                continue

            qty = inventory_levels[0].get("available", 0)

            # Apply stock to the product using stock.quant
            quant = self.env['stock.quant'].search([
                ('product_id', '=', product.id),
                ('location_id', '=', location.id)
            ], limit=1)

            if quant:
                quant.inventory_quantity = qty
                quant._apply_inventory()
                _logger.info(f"✅ Stock updated for '{product.name}' → {qty}")
            else:
                self.env['stock.quant'].create({
                    'product_id': product.id,
                    'location_id': location.id,
                    'inventory_quantity': qty,
                })._apply_inventory()
                _logger.info(f"✅ Stock created for '{product.name}' → {qty}")
