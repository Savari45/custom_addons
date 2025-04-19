import json
import requests
from odoo import http
from odoo.http import request


class WhatsAppShoppingBot(http.Controller):

    @http.route('/whatsapp/webhook', type='json', auth='public', methods=['POST'])
    def whatsapp_webhook(self, **kwargs):
        data = json.loads(request.httprequest.data)

        messages = data.get('messages', [])
        if not messages:
            return {'status': 'no_messages'}

        message = messages[0].get('text', {}).get('body', '')
        customer_phone = data.get('contacts', [{}])[0].get('wa_id', '')

        response = self.process_message(customer_phone, message)
        self.send_whatsapp_message(customer_phone, response)

        return {"status": "message_processed"}

    def process_message(self, phone, message):
        user_state = self.get_user_state(phone)

        if message.lower() in ["hi", "hello"]:
            self.set_user_state(phone, "main_menu")
            return "👋 Hi! Welcome to XYZ Store. Type:\n1️⃣ Browse Products\n2️⃣ View Cart\n3️⃣ Place Order"

        elif user_state == "main_menu":
            if message == "1":
                self.set_user_state(phone, "choose_category")
                return "🛒 Choose a category:\n1️⃣ Electronics\n2️⃣ Clothing\n3️⃣ Home Appliances"
            elif message == "2":
                return self.view_cart(phone)
            elif message == "3":
                return self.place_order(phone)
            return "Invalid option. Please type 1, 2, or 3."

        elif user_state == "choose_category":
            category = self.get_category_name(message)
            if category:
                self.set_user_state(phone, f"browse_products:{category}")
                return self.show_products(category)
            return "Invalid category. Type a valid number."

        elif user_state.startswith("browse_products"):
            category = user_state.split(":")[1]
            product = self.get_product_name(category, message)
            if product:
                self.add_to_cart(phone, product)
                return f"✅ {product} added to cart. Type 'cart' to view or 'checkout' to place an order."
            return "Invalid product selection."

        elif message.lower() == "cart":
            return self.view_cart(phone)

        elif message.lower() == "checkout":
            return self.place_order(phone)

        return "I didn't understand. Type 'hi' to start."

    def get_user_state(self, phone):
        user = request.env['whatsapp.bot.session'].sudo().search([('phone', '=', phone)], limit=1)
        return user.state if user else "new"

    def set_user_state(self, phone, state):
        session = request.env['whatsapp.bot.session'].sudo().search([('phone', '=', phone)], limit=1)
        if session:
            session.write({'state': state})
        else:
            request.env['whatsapp.bot.session'].sudo().create({'phone': phone, 'state': state})

    def get_category_name(self, option):
        categories = {"1": "Electronics", "2": "Clothing", "3": "Home Appliances"}
        return categories.get(option, None)

    def show_products(self, category):
        products = request.env['product.product'].sudo().search([('categ_id.name', '=', category)], limit=5)
        product_list = "\n".join([f"{i + 1}️⃣ {p.name} - ₹{p.lst_price}" for i, p in enumerate(products)])
        return f"📌 Products in {category}:\n{product_list}\nType the number to add a product."

    def add_to_cart(self, phone, product):
        session = request.env['whatsapp.bot.session'].sudo().search([('phone', '=', phone)], limit=1)
        if session:
            session.write({'cart': f"{session.cart},{product}" if session.cart else product})

    def view_cart(self, phone):
        session = request.env['whatsapp.bot.session'].sudo().search([('phone', '=', phone)], limit=1)
        if not session or not session.cart:
            return "🛒 Your cart is empty. Type '1' to browse products."

        cart_items = session.cart.split(',')
        formatted_cart = "\n".join(cart_items)  # Correct way to add line breaks
        return f"🛍 Your cart:\n{formatted_cart}"

    def place_order(self, phone):
        session = request.env['whatsapp.bot.session'].sudo().search([('phone', '=', phone)], limit=1)
        if not session or not session.cart:
            return "❌ No items in cart. Browse products first."

        customer = request.env['res.partner'].sudo().search([('mobile', '=', phone)], limit=1)
        if not customer:
            customer = request.env['res.partner'].sudo().create({'name': f'WhatsApp Customer {phone}', 'mobile': phone})

        order_lines = []
        for product_name in session.cart.split(","):
            product = request.env['product.product'].sudo().search([('name', 'ilike', product_name)], limit=1)
            if product:
                order_lines.append((0, 0, {'product_id': product.id, 'product_uom_qty': 1}))

        sale_order = request.env['sale.order'].sudo().create({'partner_id': customer.id, 'order_line': order_lines})
        session.write({'cart': ""})
        return f"✅ Order {sale_order.name} placed successfully!"

    def send_whatsapp_message(self, phone, message):
        pass  # Integrate with WhatsApp API
