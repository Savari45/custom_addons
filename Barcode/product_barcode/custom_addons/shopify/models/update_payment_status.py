import requests
from odoo import models, fields, _

from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    shopify_order_id = fields.Char(string='Shopify Order ID')


    def cron_push_payments_to_shopify(self):
        invoices = self.search([
            ('state', '=', 'posted'),
            ('move_type', '=', 'out_invoice'),
            ('shopify_order_id', '!=', False)
        ])
        for invoice in invoices:
            invoice.push_payment_to_shopify()

    def push_payment_to_shopify(self):
        if not self.shopify_order_id:
            print(f"⚠️ Invoice {self.name} has no Shopify Order ID. Skipping...")
            return False

        instance = self.env['shopify.instance'].search([], limit=1)
        if not instance:
            _logger.error("❌ No Shopify instance found in the system.")
            return

        domain = instance.shopify_domain
        token = instance.shopify_token


        if not domain or not token:
            raise UserError(_("Shopify domain or token is missing in the linked instance."))

        shop_url = f"https://{domain}/admin/api/2025-04/graphql.json"

        query = """
        mutation orderMarkAsPaid($input: OrderMarkAsPaidInput!) {
          orderMarkAsPaid(input: $input) {
            order {
              id
              displayFinancialStatus
            }
            userErrors {
              field
              message
            }
          }
        }
        """
        variables = {
            "input": {
                "id": f"gid://shopify/Order/{self.shopify_order_id}"
            }
        }

        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": token,
        }

        try:
            print(f"🔹 Marking Shopify Order {self.shopify_order_id} as paid via GraphQL…")
            response = requests.post(
                shop_url,
                json={"query": query, "variables": variables},
                headers=headers,
                timeout=50
            )
            response.raise_for_status()
            data = response.json()

            if data.get("errors"):
                msgs = [e["message"] for e in data["errors"]]
                raise UserError(_("Shopify GraphQL Error:\n%s") % "\n".join(msgs))

            payload = data["data"]["orderMarkAsPaid"]
            if payload["userErrors"]:
                msgs = [e["message"] for e in payload["userErrors"]]
                print(f"⚠️ Shopify userErrors: {msgs}")
                return False

            status = payload["order"]["displayFinancialStatus"]
            print(f"✅ Shopify Order {self.shopify_order_id} marked as paid. Status: {status}")
            return True

        except requests.RequestException as e:
            raise UserError(_("Failed to connect to Shopify: %s") % str(e))
