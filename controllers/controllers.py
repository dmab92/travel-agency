# -*- coding: utf-8 -*-
# from odoo import http


# class ColisApp(http.Controller):
#     @http.route('/colis_app/colis_app/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/colis_app/colis_app/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('colis_app.listing', {
#             'root': '/colis_app/colis_app',
#             'objects': http.request.env['colis_app.colis_app'].search([]),
#         })

#     @http.route('/colis_app/colis_app/objects/<model("colis_app.colis_app"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('colis_app.object', {
#             'object': obj
#         })
