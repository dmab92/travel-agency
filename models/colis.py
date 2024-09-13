# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from odoo import api, fields, models, SUPERUSER_ID, _
import time
import urllib, requests, re
from datetime import datetime
from odoo.exceptions import UserError, Warning, ValidationError

from urllib.parse import urljoin, urlparse


visited_urls = set()

class voyage_colis(models.Model):
    """Defining model for radio camando."""
    _description = 'Envoi des Colis'
    _name = 'voyage.colis'
    _rec_name = 'numero_colis'
    _order = 'id DESC'

    def _get_next_reference(self):
        query = """SELECT COUNT(id) AS ligne FROM voyage_colis"""
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

        if data < 10000 and data >= 1000:
            return '0' + str(data + 1) + '/' + sort_year

        if data < 100000 and data >= 10000:
            return '' + str(data + 1) + '/' + sort_year

    numero_colis = fields.Char("Numero du colis", readonly="True", default=lambda self: self._get_next_reference())
    date_register = fields.Datetime('Date d\'énregistrement du colis', default=fields.datetime.now())
    sender_id = fields.Many2one('res.partner', "Nom de l'expediteur")
    user_id = fields.Many2one('res.users', 'Guichetier(e)', default=lambda self: self.env.user)
    sender_phone = fields.Char("Telephone")
    sender_date = fields.Date("Date d'envoi", default=datetime.today())
    receive_id = fields.Many2one('res.partner', "Destinataire du colis")
    receive_phone = fields.Char("Telephone")
    receive_date = fields.Date("Date de retrait")
    price = fields.Integer("Montant Payé")
    contenu_colis = fields.Text("Nature du colis")
    state = fields.Selection([('draft', 'Non Recupéré'),
                              ('send', 'Recupéré')
                               ],
                             string='Etat', default='draft',
                             help="Il s'agit de l'Etat du colis, il peut etre A envoyer, Envoyé ou Recu")

    ville_envoi_id = fields.Many2one('ville.envoi.colis', "Ville d'envoi")
    ville_reception_id = fields.Many2one('ville.recept.colis', "Ville de reception")
    info_excat = fields.Boolean("Est vous sur de vouloir valider l'envoi du colis ?", defaut=False)
    cni_exp = fields.Char("CNI")
    valeur_colis = fields.Integer("Valeur du Colis (FCFA)")
    api_key = fields.Char("Api Key")
    senderID = fields.Char("SendeID")
    borderau_id = fields.Many2one('borderau.colis',string='Borderau')

    # phone_id = fields.Many2one("voyage.passager")
    # nom = fields.Char(related='phone_id.partner_id.name')
    # cni = fields.Char(related='phone_id.cni')

    def send_colis_sms(self):

        for record in self:
            if not record.price:
                raise UserError(_("Veillez saisir les frais d'envoi du colis"))
            if not record.valeur_colis:
                raise UserError(
                    _("Veillez  entrez la valeur déclarée du Colis"))
            if record.info_excat == False:
                raise UserError(
                    _("Veillez certifier que ces informations sont exactes avant de valider l'envoi du colis"))

        # SMS a l'expediteur
        # api_key = 'b0l5cGl6TE5JZmt6ZkdIZEZsTUQ='
        # url = 'https://app.techsoft-web-agency.com/sms/api'
        # senderID = self.senderID
        #
        # destination = str(self.receive_phone)
        # message = str(self.sexe_rec) + "" + self.receive_id.name + " votre  colis " + str(
        #     self.numero_colis) + " contenant " \
        #           + str(self.contenu_colis) + " vient d'etre expedié  depuis " + str(
        #     self.ville_envoi_id.name) + " par " + str(self.sexe) + "" + str(
        #     self.sender_id.name) + " Veillez passer a l'agence pour le recuperer.Infoline au " + str(
        #     self.user_id.company_id.phone)
        # # ".Veuillez passer a partir du " +str(self.receive_date.strftime('%d/%m/%Y')) + \
        #
        # sms_body = {
        #     'action': 'send-sms',
        #     'api_key': api_key,
        #     'to': destination,
        #     'from': senderID,
        #     'sms': message
        # }
        # final_url2 = url + "?" + urllib.parse.urlencode(sms_body)
        # requests.get(final_url2)

        return self.write({'state': 'send'})

    def receive_colis_sms(self):
        # if not self.digital_signature:
        #     raise UserError(_("Veillez faire signer le destinataire du avant de valider la reception"))

        # Notification SMS a  l'expediteur
        # api_key = 'b0l5cGl6TE5JZmt6ZkdIZEZsTUQ='
        # url = 'https://app.techsoft-web-agency.com/sms/api'
        # senderID = 'DJAMA AIR'
        # destination = str(self.sender_phone)
        # message = str(self.sexe) + "" + self.sender_id.name + " votre colis " + str(
        #     self.numero_colis) + " vient d'etre retirer par le destinataire. Merci de faire confiance a " + str(
        #     self.user_id.company_id.name)
        #
        # sms_body = {
        #     'action': 'send-sms',
        #     'api_key': api_key,
        #     'to': destination,
        #     'from': senderID,
        #     'sms': message
        # }
        # final_url1 = url + "?" + urllib.parse.urlencode(sms_body)
        # requests.get(final_url1)

        # destination = str(self.receive_phone)
        # message = "M./Mme " + self.receive_id.name + "vous venez de retirer votre colis " + str(self.numero_colis) + "Merci de faire confiance a " +str(self.user_id.company_id.name)
        # sms_body = {
        #     'action': 'send-sms',
        #     'api_key': api_key,
        #     'to': destination,
        #     'from': senderID,
        #     'sms': message
        # }
        # final_url2 = url + "?" + urllib.parse.urlencode(sms_body)
        # requests.get(final_url2)

        return self.write({'state': 'receive'})

    def print_ticket(self):
        return self.env.ref('travel_agency_app.action_report_ticket_colis').report_action(self)

    def set_to_draft(self):
        return self.write({'state': 'draft'})

    def set_to_send(self):
        return self.write({'state': 'send'})




class borderau_colis(models.Model):
    """Defining model for radio camando."""
    _description = 'Bordeau d''envoi des Colis'
    _name = 'borderau.colis'
    _rec_name = 'num_bordereau'
    _order = 'id DESC'

    def _get_next_reference(self):
        query = """SELECT COUNT(id) AS ligne FROM borderau_colis"""
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

        if data < 10000 and data >= 1000:
            return '0' + str(data + 1) + '/' + sort_year

        if data < 100000 and data >= 10000:
            return '' + str(data + 1) + '/' + sort_year

    num_bordereau = fields.Char("Numero du Bordeau", readonly="True", default = lambda self: self._get_next_reference())
    date_register = fields.Datetime('Date d\'énregistrement du colis', default=fields.datetime.now())
    index = fields.Char('Index')

    state = fields.Selection([('draft', 'Brouillon'),
                              ('send', 'Validé')
                              ],
                             string='Etat', default='draft',
                             help="Il s'agit de l'Etat du colis, il peut etre A envoyer, Envoyé ou Recu")

    ville_envoi_id = fields.Many2one('ville.envoi.colis', "Depart")
    ville_reception_id = fields.Many2one('ville.recept.colis', "Destination")
    coli_ids = fields.One2many('voyage.colis','borderau_id', string='Colis')
    price_total = fields.Integer("Total Encaissé", compute='_compute_colis', digits=0)
    driver_id = fields.Many2one("res.partner", "Conducteur", )
    user_id = fields.Many2one('res.users', 'Guichetier(e)', default=lambda self: self.env.user)
    car_id = fields.Many2one("fleet.vehicle", "Vehicule")
    info_excat = fields.Boolean("Est vous sur de vouloir valider l'envoi du colis ?", defaut=False)

    @api.onchange('coli_ids')
    def _compute_colis(self):
        """Compute the invoice count"""
        for record in self:
            record.price_total = sum(record.coli_ids.mapped('price'))

    def print_bordeau_colis(self):
        if not  self.info_excat:
            raise UserError(
                _("Veillez certifier que ces informations sont exactes avant de valider  l'impression du Bordereau"))
        self.write({'state': 'send'})
        return self.env.ref('travel_agency_app.action_bordereau_colis').report_action(self)

    def set_to_draft(self):
        return self.write({'state': 'draft'})













