# -*- coding: utf-8 -*-
# from odoo import http


# class PosMarginSale(http.Controller):
#     @http.route('/pos_margin_threshold/pos_margin_threshold', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_margin_threshold/pos_margin_threshold/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_margin_threshold.listing', {
#             'root': '/pos_margin_threshold/pos_margin_threshold',
#             'objects': http.request.env['pos_margin_threshold.pos_margin_threshold'].search([]),
#         })

#     @http.route('/pos_margin_threshold/pos_margin_threshold/objects/<model("pos_margin_threshold.pos_margin_threshold"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_margin_threshold.object', {
#             'object': obj
#         })

