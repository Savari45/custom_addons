# -*- coding: utf-8 -*-
# from odoo import http


# class SaleFullDelivery(http.Controller):
#     @http.route('/sale_full_delivery/sale_full_delivery', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_full_delivery/sale_full_delivery/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_full_delivery.listing', {
#             'root': '/sale_full_delivery/sale_full_delivery',
#             'objects': http.request.env['sale_full_delivery.sale_full_delivery'].search([]),
#         })

#     @http.route('/sale_full_delivery/sale_full_delivery/objects/<model("sale_full_delivery.sale_full_delivery"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_full_delivery.object', {
#             'object': obj
#         })

