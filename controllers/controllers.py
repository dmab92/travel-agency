# -*- coding: utf-8 -*-
# from odoo import http


# class ColisApp(http.Controller):
#     @http.route('/travel_agency_app/travel_agency_app/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/travel_agency_app/travel_agency_app/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('travel_agency_app.listing', {
#             'root': '/travel_agency_app/travel_agency_app',
#             'objects': http.request.env['travel_agency_app.travel_agency_app'].search([]),
#         })

#     @http.route('/travel_agency_app/travel_agency_app/objects/<model("travel_agency_app.travel_agency_app"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('travel_agency_app.object', {
#             'object': obj
#         })
