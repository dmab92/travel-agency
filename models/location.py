# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError
import time


class location_vehicule(models.Model):
    """Defining model for voyage."""
    _name = 'location.vehicule'
    _description = 'Loctions des Bus'
    _rec_name = 'name'
    _order = 'id DESC'

    def _get_next_reference(self):
        query = """SELECT COUNT(id) AS ligne FROM location_vehicule"""
        self.env.cr.execute(query)
        data = self.env.cr.fetchone()[0]
        year = time.strftime('%Y')
        sort_year = ''

        # on recupère les 2 derniers chiffres
        y = 0
        for i in year:
            y += 1
            if y < 3:
                continue
            sort_year = sort_year + str(i)

        if not data or data == 0:
            return '00001/' + sort_year

        if data < 10:
            return '0000' + str(data + 1) + '/' + sort_year

        if data < 100 and data >= 10:
            return '000' + str(data + 1) + '/' + sort_year

    name = fields.Char("Numero  de la Location",readonly="True", default = lambda self: self._get_next_reference())
    date_register = fields.Datetime('Date de location', default=fields.datetime.now())
    date_debut = fields.Datetime('Depart Prevu le')
    date_fin = fields.Datetime('Retour le :')

    departure_id = fields.Many2one("ville.envoi.colis", " Depart", )
    destination_id = fields.Many2one("ville.recept.colis", "Destination")

    price = fields.Integer("Montant de la location", digits=(6, 0))
    car_id = fields.Many2one("fleet.vehicle", "Vehicule")
    driver_id = fields.Many2one("res.partner", "Conducteur", )
    ration = fields.Integer("Ration Chauffeur", digits=0)
    road_fees = fields.Integer("Frais de route", digits=0)
    partner_id = fields.Many2one("res.partner", "Locataire", required=1)
    phone = fields.Char("Telephone", related='partner_id.phone')
    cni = fields.Char("CNI")
    notice = fields.Text("Notice")
    user_id = fields.Many2one("res.users", "Recu par", default=lambda self: self.env.user)

    state = fields.Selection([('draft', 'Brouillon'),
                               ('send', 'Validée'),
                               ('cancel', 'Annulée'),
                               ], require=1, default='draft',
                              string='Etat')

    confirm = fields.Boolean("Je confirme avoir reelu cette fiche et n'avoir apercu aucune anomalie")

    def set_valited(self):
        if not self.confirm:
            raise UserError(
                _("'Alert !!! Veuillez  confirmer l'exactude des ces informations avant de les valider'"))

        self.write({'state': 'send'})
        return self.env.ref('travel_agency_app.action_report_location').report_action(self)

    def set_draft(self):
        if not self.confirm:
            raise UserError(
                _("'Alert !!! Veuillez  confirmer l'exactude des ces informations avant de les valider'"))

        return self.write({'state': 'draft'})

    def set_cancel(self):
        return self.write({'state': 'cancel'})



    def print_recu(self):
        return self.write({'state': 'cancel'})