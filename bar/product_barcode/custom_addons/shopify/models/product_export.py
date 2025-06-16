import logging
import requests
import base64
from odoo import models, fields

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    shopify_product_id = fields.Char("Shopify Product ID", copy=False)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    shopify_variant_id = fields.Char("Shopify Variant ID", copy=False)
    shopify_inventory_item_id = fields.Char("Shopify Inventory Item ID", copy=False)


class ShopifyProductExport(models.Model):
    _name = 'shopify.product.export'
    _description = 'Push Odoo Products to Shopify'

    def push_products_to_shopify(self):
        # Get Shopify instance details
        instance = self.env['shopify.instance'].search([], limit=1)
        if not instance:
            _logger.error("No Shopify instance configured.")
            return

        headers = {
            'X-Shopify-Access-Token': instance.shopify_token,
            'Content-Type': 'application/json',
        }

        templates = self.env['product.template'].search([
            ('sale_ok', '=', True),
            ('purchase_ok', '=', False)
        ])

        for template in templates:
            skip_due_to_sku = False

            # 🔍 Check if any variant's SKU exists on Shopify
            for variant in template.product_variant_ids:
                sku = variant.default_code
                if not sku:
                    continue

                try:
                    # Shopify API to fetch existing products with variants (limit 250)
                    check_url = f"https://{instance.shopify_domain}/admin/api/2023-10/products.json?fields=variants&limit=250"
                    response = requests.get(check_url, headers=headers)
                    response.raise_for_status()
                    products = response.json().get("products", [])

                    for prod in products:
                        for shopify_variant in prod.get("variants", []):
                            if shopify_variant.get("sku") == sku:
                                _logger.warning(f"⚠️ SKU {sku} already exists on Shopify. Skipping product '{template.name}'.")
                                skip_due_to_sku = True
                                break
                        if skip_due_to_sku:
                            break
                except Exception as e:
                    _logger.error(f"❌ Error while checking SKU {sku} on Shopify: {e}")

                if skip_due_to_sku:
                    break

            if skip_due_to_sku:
                continue

            # Build Shopify options (attributes)
            attribute_lines = template.attribute_line_ids
            option_names = [line.attribute_id.name for line in attribute_lines]
            options_payload = [{"name": name} for name in option_names] if option_names else [
                {"name": "Title", "values": ["Default Title"]}]
            images_payload = []

            # Main image
            if template.image_1920:
                img_base64 = base64.b64encode(template.image_1920).decode('utf-8')
                images_payload.append({"attachment": img_base64})

            # Variants logic
            variants_payload = []
            for variant in template.product_variant_ids:
                # Collect option values in order
                option_values = []
                for line in attribute_lines:
                    val = variant.product_template_attribute_value_ids.filtered(
                        lambda x: x.attribute_id == line.attribute_id)
                    option_values.append(val.name if val else "")
                # Single variant case
                if not option_values:
                    option_values = ["Default Title"]

                variant_payload = {
                    "sku": variant.default_code or "",
                    "barcode": variant.barcode or "",
                    "price": variant.lst_price,
                    "inventory_quantity": int(variant.qty_available),
                    "inventory_management": "shopify",
                }
                # Add options
                for i, value in enumerate(option_values):
                    variant_payload[f"option{i + 1}"] = value
                variants_payload.append(variant_payload)

            product_data = {
                "product": {
                    "title": template.name,
                    "body_html": template.description_sale or '',
                    "variants": variants_payload,
                    "images": images_payload,
                    "options": options_payload,
                }
            }

            try:
                # Create product
                url = f"https://{instance.shopify_domain}/admin/api/2023-10/products.json"
                response = requests.post(url, headers=headers, json=product_data)
                response.raise_for_status()
                shopify_product = response.json().get('product')
                if shopify_product:
                    template.shopify_product_id = shopify_product['id']
                    _logger.info(f"✅ Exported product '{template.name}' with variants to Shopify.")
            except Exception as post_error:
                _logger.error(f"❌ Failed to push {template.name}: {post_error}")
