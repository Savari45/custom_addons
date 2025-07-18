import requests

from odoo import models, fields, _


class PosOrder(models.Model):
    _inherit = 'pos.order'

    whatsapp_url = fields.Char(string="WhatsApp Message Link", compute='_compute_whatsapp_url')

    def action_pos_order_paid(self):
        print("ffffffffffffffffffffffff")
        res = super().action_pos_order_paid()

        for order in self:
            partner = order.partner_id
            if partner and partner.phone:
                number = partner.phone.replace("+", "").replace(" ", "")
                amount = order.amount_total
                order_lines = order.lines

                # Format product details
                products = ""
                for line in order_lines:
                    products += f"- {line.product_id.display_name} × {line.qty} = ₹{line.price_subtotal:.2f}\n"

                message = (
                    f"Hi {partner.name},\n\n"
                    f"🧾 *Your Order {order.name} Details:*\n"
                    f"{products}\n"
                    f"🧮 *Total: ₹{amount:.2f}*\n\n"
                    f"Thank you for shopping with us!"
                )
                print("message",message)

                encoded_msg = requests.utils.quote(message)
                wa_link = f"https://wa.me/{number}?text={encoded_msg}"
                print(wa_link)

                # You can't open this from backend. But you can store it in the order:
                order.whatsapp_url = wa_link
                print(order.whatsapp_url)

        return res

    def _compute_whatsapp_url(self):
        print("hhhhhhhhhhhhhhhhhhh")
        for order in self:
            partner = order.partner_id
            if partner and partner.phone:
                number = partner.phone.replace("+", "").replace(" ", "")
                amount = order.amount_total
                order_lines = order.lines

                products = ""
                for line in order_lines:
                    products += f"- {line.product_id.display_name} × {line.qty} = ₹{line.price_subtotal:.2f}\n"

                message = (
                    f"Hi {partner.name},\n\n"
                    f"🧾 *Your Order {order.name} Details:*\n"
                    f"{products}\n"
                    f"🧮 *Total: ₹{amount:.2f}*\n\n"
                    f"Thank you!"
                )

                import requests
                encoded_msg = requests.utils.quote(message)
                order.whatsapp_url = f"https://wa.me/{number}?text={encoded_msg}"
            else:
                order.whatsapp_url = False
