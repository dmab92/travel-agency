# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
import time
import urllib, requests
from datetime import datetime as dt
from odoo.exceptions import UserError, Warning, ValidationError


class vehicule_voyage(models.Model):
    """Defining model for voyage."""
    _name = 'vehicule.voyage'
    _description = ' Vehicule de voyage'
    _rec_name = 'name'
    _order = 'id DESC'

    def _get_next_reference(self):
        query = """SELECT COUNT(id) AS ligne FROM vehicule_voyage"""
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

        if data < 1000 and data >= 100:
            return '00' + str(data + 1) + '/' + sort_year

    name = fields.Char("No d'enregistrement", readonly="True", default=lambda self: self._get_next_reference())

    date_register = fields.Datetime(string='Date et Heure d''enregistrement', default=fields.datetime.now())
    car_id = fields.Many2one("fleet.vehicle", string="Vehicule", required=1)
    dossiers_ids = fields.One2many('dossier.vehicule', 'vehicule_id', string="Pieces du Dossier")

    date_grise_e = fields.Date('Date d''Emission')
    date_grise_expi = fields.Date('Date d''Expritaion')
    validity_gris = fields.Integer("Validité(Années)", default=10)

    date_blue_e = fields.Date('Date d''emission')
    date_blue_expi = fields.Date('Date d''Expritaion')
    validity_bleu = fields.Integer("Validité(Années)", default=1)

    date_visit_e = fields.Date('Date d''emission')
    date_visit_expi = fields.Date('Date d''Expritaion')
    validity_visit = fields.Integer("Validité(Années)", default=1)

    date_lic_e = fields.Date('Date d''emission')
    date_lic_expi = fields.Date('Date d''Expritaion')
    validity_lic = fields.Integer("Validité(Années)", default=5)

    date_agre_e = fields.Date('Date d''emission')
    date_agre_expi = fields.Date('Date d''Expritaion')
    validity_agre = fields.Integer("Validité(Années)", default=2)

    date_certif_e = fields.Date('Date d''emission')
    date_certif_expi = fields.Date('Date d''Expritaion')
    validity_cert = fields.Integer("Validité(Années)", default=2)

    date_assur_e = fields.Date('Date d''emission')
    date_assur_expi = fields.Date('Date d''Expritaion')
    validity_assur = fields.Integer("Validité(Années)", default=1)

    date_fisc_e = fields.Date('Date d''emission')
    date_fisc_expi = fields.Date('Date d''Expritaion')
    validity_fisc = fields.Integer("Validité(Années)", default=1)

    state = fields.Selection([('draft', 'brouillon'),
                              ('send', 'Valider')], default='draft', string='Etat')

    destination = fields.Char("Destinataire")

    # @api.model
    # def default_get(self, fields_list):
    #     res = super(vehicule_voyage, self).default_get(fields_list)
    #     lignes_ids = self.env['dossier.vehicule'].search([])
    #     lines = [(5, 0, 0)]
    #     for rec in self:
    #         for line in lignes_ids:
    #             vals = {
    #                 'vehicule_id': line.id,
    #                 'name': line.name,
    #                 'validity': line.validity,
    #                 'state': line.state
    #             }
    #             lines.append((0, 0, vals))
    #     res.update({'dossiers_ids': lines})
    #     return res

    def upload_car_doc(self):

        lignes_ids = self.env['dossier.vehicule'].search([])
        if len(lignes_ids) == 0:
            raise UserError(_("'Alert !!! Veillez enregistrement au moins une piece dans les configurations'"))
        for rec in self:
            if rec.car_id:
                lines = [(5, 0, 0)]
                for line in lignes_ids:
                    vals = {
                        'vehicule_id': line.id,
                        'name': line.name,
                        'validity': line.validity,
                        'state': line.state
                    }
                    lines.append((0, 0, vals))
            rec.dossiers_ids = lines

    def send_sms(self):
        vehicule_ids = self.env['vehicule.voyage'].search([])
        limit =[14,7,3]
        api_key = 'b0l5cGl6TE5JZmt6ZkdIZEZsTUQ='
        url = 'https://app.techsoft-web-agency.com/sms/api'
        senderID = 'DJAMA AIR'
        #destination = str(self.destination)
        destination =self.destination
        #limit=7
        for vehicule in vehicule_ids:
            if (vehicule.date_grise_expi - dt.now().date()).days in limit:
                # SMS a l'expediteur

                message = "ATTENTION la Carte Grise du Vehicule " + str(vehicule.car_id.license_plate) + " expire le " \
                          + str(dt.strptime(str(vehicule.date_grise_expi), '%Y-%m-%d'))+ " Veillez penser à la renouveller !! "
                # message = " Ceci est un test pour le service de transport "
                sms_body = {
                    'action': 'send-sms',
                    'api_key': api_key,
                    'to': destination,
                    'from': senderID,
                    'sms': message
                }
                final_url2 = url + "?" + urllib.parse.urlencode(sms_body)
                requests.get(final_url2)

            if (vehicule.date_blue_expi - dt.now().date()).days in limit:
                # SMS a l'expediteur
                message = " ATTENTION la Carte Blue du Vehicule " + str(vehicule.car_id.license_plate) + " expire le " \
                          + str(dt.strptime(str(vehicule.date_blue_expi), '%Y-%m-%d')) + " Veillez penser à la renouveller !! "
                # message = " Ceci est un test pour le service de transport "

                sms_body = {
                    'action': 'send-sms',
                    'api_key': api_key,
                    'to': destination,
                    'from': senderID,
                    'sms': message
                }
                final_url2 = url + "?" + urllib.parse.urlencode(sms_body)
                requests.get(final_url2)

            if (vehicule.date_visit_expi - dt.now().date()).days in limit:
                # SMS a l'expediteur
                message = " ATTENTION la Visite Technique du Vehicule " + str(vehicule.car_id.license_plate) + " expire le " \
                          + str(dt.strptime(str(vehicule.date_visit_expi), '%Y-%m-%d')) + " Veillez penser à la renouveller !! "
                # message = " Ceci est un test pour le service de transport "

                sms_body = {
                    'action': 'send-sms',
                    'api_key': api_key,
                    'to': destination,
                    'from': senderID,
                    'sms': message
                }
                final_url2 = url + "?" + urllib.parse.urlencode(sms_body)
                requests.get(final_url2)

            if (vehicule.date_lic_expi - dt.now().date()).days in limit:
                # SMS a l'expediteur
                message = " ATTENTION la Licence du Vehicule " + str(vehicule.car_id.license_plate) + " expire le " \
                          + str(dt.strptime(str(vehicule.date_lic_expi), '%Y-%m-%d')) + " Veillez penser à la renouveller !! "
                # message = " Ceci est un test pour le service de transport "

                sms_body = {
                    'action': 'send-sms',
                    'api_key': api_key,
                    'to': destination,
                    'from': senderID,
                    'sms': message
                }
                final_url2 = url + "?" + urllib.parse.urlencode(sms_body)
                requests.get(final_url2)

            if (vehicule.date_agre_expi - dt.now().date()).days in limit:
                # SMS a l'expediteur
                message = " ATTENTION L'agremement du Vehicule " + str(vehicule.car_id.license_plate) + " expire le " \
                          + str(dt.strptime(str(vehicule.date_agre_expi), '%Y-%m-%d')) + " Veillez penser à la renouveller !! "
                # message = " Ceci est un test pour le service de transport "

                sms_body = {
                    'action': 'send-sms',
                    'api_key': api_key,
                    'to': destination,
                    'from': senderID,
                    'sms': message
                }
                final_url2 = url + "?" + urllib.parse.urlencode(sms_body)
                requests.get(final_url2)
            if (vehicule.date_agre_expi - dt.now().date()).days in limit:
                # SMS a l'expediteur
                message = " ATTENTION Le Certificat de JOUAGEAGE du Vehicule " + str(vehicule.car_id.license_plate) + " expire le " \
                          + str(dt.strptime(str(vehicule.date_agre_expi), '%Y-%m-%d')) + " Veillez penser à la renouveller !! "
                # message = " Ceci est un test pour le service de transport "

                sms_body = {
                    'action': 'send-sms',
                    'api_key': api_key,
                    'to': destination,
                    'from': senderID,
                    'sms': message
                }
                final_url2 = url + "?" + urllib.parse.urlencode(sms_body)
                requests.get(final_url2)

            if (vehicule.date_fisc_expi - dt.now().date()).days in limit:
                # SMS a l'expediteur
                message = " ATTENTION L'attestation de conformité Fiscale du Vehicule " + str(vehicule.car_id.license_plate) + " expire le " \
                          + str(dt.strptime(str(vehicule.date_fisc_expi), '%Y-%m-%d')) + " Veillez penser à la renouveller !! "
                # message = " Ceci est un test pour le service de transport "

                sms_body = {
                    'action': 'send-sms',
                    'api_key': api_key,
                    'to': destination,
                    'from': senderID,
                    'sms': message
                }
                final_url2 = url + "?" + urllib.parse.urlencode(sms_body)
                requests.get(final_url2)

            if (vehicule.date_assur_expi - dt.now().date()).days in limit:
                # SMS a l'expediteur
                message = " ATTENTION L'ASSURANCE du Vehicule " + str(vehicule.car_id.license_plate) + " expire le " \
                          + str(dt.strptime(str(vehicule.date_assur_expi), '%Y-%m-%d')) + " Veillez penser à la renouveller !! "
                # message = " Ceci est un test pour le service de transport "

                sms_body = {
                    'action': 'send-sms',
                    'api_key': api_key,
                    'to': destination,
                    'from': senderID,
                    'sms': message
                }
                final_url2 = url + "?" + urllib.parse.urlencode(sms_body)
                requests.get(final_url2)




class driver_voyage(models.Model):
    """Defining model for voyage."""
    _name = 'driver.voyage'
    _description = 'Camions Drivers'
    _rec_name = 'name'
    _order = 'id DESC'

    def _get_next_reference(self):
        query = """SELECT COUNT(id) AS ligne FROM driver_voyage"""
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

        if data < 1000 and data >= 100:
            return '00' + str(data + 1) + '/' + sort_year

    name = fields.Char("No d'enregistrement", readonly="True", default=lambda self: self._get_next_reference())

    date_register = fields.Datetime('Date d''enregistrement', default=fields.datetime.now())
    driver_id = fields.Many2one("res.partner", "Chauffeur", required=1)

    # doc_chauf_ids = fields.One2many('dossier.chaffeur', 'driver_id', string="Pieces du Dossier")

    date_permis_e = fields.Date('Date d''Emission')
    date_permis_expi = fields.Date('Date d''Expritaion')

    date_cni_e = fields.Date('Date d''emission')
    date_cni_expi = fields.Date('Date d''Expritaion')

    date_scdp_e = fields.Date('Date d''emission')
    date_scpd_expi = fields.Date('Date d''Expritaion')
    state = fields.Selection([('draft', 'brouillon'),
                              ('send', 'Valider')], default='draft', string='Etat')

    def upload_driver_doc(self):
        pass
