# -*- coding: utf-8 -*-
import requests
import logging
import base64
import time
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ShopifyStockExport(models.Model):
    _name = 'shopify.stock.export'
    _description = 'Export Odoo Product Stock to Shopify'

    def export_stock_to_shopify(self):
        instance = self.env['shopify.instance'].search([], limit=1)
        if not instance:
            _logger.error("❌ No Shopify instance configured.")
            return

        domain = instance.shopify_domain
        token = instance.shopify_token
        headers = {
            "X-Shopify-Access-Token": token,
            "Content-Type": "application/json"
        }

        products = self.env['product.product'].search([('default_code', '!=', False)])
        for product in products:
            sku = product.default_code
            inventory_item_id = self.env['account.move'].get_shopify_inventory_item_id(domain, token, sku)
            if not inventory_item_id:
                continue
            qty = product.with_context(location=instance.stock_location_id.id).qty_available
            payload = {
                "location_id": instance.shopify_location_id,
                "inventory_item_id": inventory_item_id,
                "available": int(qty)
            }
            url = f"https://{domain}/admin/api/2023-01/inventory_levels/set.json"
            try:
                resp = requests.post(url, headers=headers, json=payload)
                if resp.status_code == 200:
                    _logger.info(f"✅ Stock for SKU {sku} set to {qty} in Shopify")
                else:
                    _logger.warning(f"❌ Failed to update stock for SKU {sku}: {resp.text}")
            except Exception as e:
                _logger.exception(f"Error exporting stock for SKU {sku}")
