import requests
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError, UserError
import requests
import logging

_logger = logging.getLogger(__name__)


class ShopifyInstance(models.Model):
    _name = 'shopify.instance'
    _description = "Shopify Instance"

    name = fields.Char("Instance Name")
    shopify_domain = fields.Char(string='Domain')
    shopify_token = fields.Char(string='Token',required=True)
    api_key = fields.Char(string='API Key')
    api_secret_key = fields.Char(string='API Secret Key')
    webhooks_secret_key = fields.Char(string='Webhooks Key')
    shopify_location_id = fields.Char(string="Shopify Location ID")
    stock_location_id = fields.Many2one('stock.location', string="Odoo Stock Location")  # ✅

    def check_shopify_credentials(self):
        for record in self:
            if not record.shopify_domain or not record.shopify_token:
                raise ValidationError("Domain or Token is missing.")

            url = f"https://{record.shopify_domain}/admin/api/2023-01/products.json"
            headers = {
                "X-Shopify-Access-Token": record.shopify_token
            }

            response = requests.get(url, headers=headers)

            if response.status_code == 401:
                raise ValidationError("Token is invalid or expired.")
            elif response.status_code != 200:
                raise ValidationError(f"Unexpected error: {response.status_code} - {response.text}")

