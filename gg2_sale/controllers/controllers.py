# -*- coding: utf-8 -*-
from odoo import http

# class Gg2(http.Controller):
#     @http.route('/gg2/gg2/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/gg2/gg2/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('gg2.listing', {
#             'root': '/gg2/gg2',
#             'objects': http.request.env['gg2.gg2'].search([]),
#         })

#     @http.route('/gg2/gg2/objects/<model("gg2.gg2"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('gg2.object', {
#             'object': obj
#         })
