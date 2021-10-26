# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
import time, random
import datetime
import urllib, requests
from datetime import datetime
from odoo.exceptions import UserError, Warning, ValidationError

class colis_colis(models.Model):
    """Defining model for radio camando."""
    _description = 'Envoi des Colis'
    _name = 'colis.colis'
    _rec_name ='numero_colis'

    def _get_next_reference(self):
        query = """SELECT COUNT(id) AS ligne FROM colis_colis"""
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
    sender_id = fields.Many2one('res.partner', "Expediteur du colis")
    sender_phone = fields.Char("Telephone", related='sender_id.mobile')
    sender_date = fields.Date("Date d'envoi",default=datetime.today())
    receive_id = fields.Many2one('res.partner', "Destinataire du colis")
    receive_phone = fields.Char("Telephone", related='receive_id.mobile')
    receive_date = fields.Date("Date de retrait programmée")
    price = fields.Integer("Frais d'envoi du colis")
    contenu_colis = fields.Text("Contenu du colis")
    state = fields.Selection([('draft', 'A Envoyer'), ('send', 'Envoyé'), ('receive', 'Recu')],
                             string='Etat', default='draft', help="Il s'agit de l'Etat du colis, il peut etre A envoyer, Envoyé ou Recu")
    ville_envoi_id = fields.Many2one('ville.envoi.colis' , "Ville d'envoi ")
    ville_reception_id = fields.Many2one('ville.recept.colis' , "Ville de reception")
    info_excat = fields.Boolean("Est vous sur de vouloir valider l'envoi du colis ?", defaut=False)

    def send_colis_sms(self):
        for record in self:
            if  not record.price :
                raise UserError(_("Veillez saisir les frais d'envoi du colis"))

            if  record.info_excat == False:
                raise UserError(_("Veillez certifier que ces informations sont exactes avant de valider l'envoi du colis"))

        #SMS a l'expediteur
        api_key='b0l5cGl6TE5JZmt6ZkdIZEZsTUQ='
        url = 'https://app.techsoft-web-agency.com/sms/api'
        #senderID = 'TESTE-DEMO'
        senderID='MTCS SARL'
        destination = str(self.sender_phone)
        message = "M./Mme " + self.sender_id.name + " votre colis numero " + str(self.numero_colis) + "contenant " \
                  + str(self.contenu_colis) + " a destination de " +str(self.ville_reception_id.name)+ " pour M./Mme" \
                  + str(self.receive_id.name) +" vient d'etre expedié. Infoline au 678128120"
        sms_body = {
            'action': 'send-sms',
            'api_key': api_key,
            'to': destination,
            'from': senderID,
            'sms': message
        }
        final_url1 = url + "?" + urllib.parse.urlencode(sms_body)
        requests.get(final_url1)

        #SMS au destinataire

        receive_date = datetime.date.strftime(receive_date, "%m/%d/%Y")
        destination = str(self.receive_phone)
        message = "M./Mme " + self.receive_id.name + "votre  colis numero " + str(self.numero_colis) + "contenant " \
                  + str(self.contenu_colis) + " vient d'etre expedié  depuis " +str(self.ville_envoi_id.name)+ " par M./Mme" +str(self.sender_id.name)+\
                  "Veillez passer dans notre agence a partir du " + str(receive_date) + \
                  " pour le recuperer. Infoline au 678128120"
        sms_body = {
            'action': 'send-sms',
            'api_key': api_key,
            'to': destination,
            'from': senderID,
            'sms': message
        }
        final_url2 = url + "?" + urllib.parse.urlencode(sms_body)
        requests.get(final_url2)

        return self.write({'state': 'send'})

    def receive_colis_sms(self):
        # Notification SMS a  l'expediteur
        api_key = 'b0l5cGl6TE5JZmt6ZkdIZEZsTUQ='
        url = 'https://app.techsoft-web-agency.com/sms/api'
        # senderID = 'TESTE-DEMO'
        senderID = 'MTCS SARL'
        destination = str(self.sender_phone)
        message = "M./Mme " + self.sender_id.name + " votre colis numero " + str(self.numero_colis) + "\
        vient d'etre retirer par le destinataire. Merci de faire confiance a MTCS SARL."

        sms_body = {
            'action': 'send-sms',
            'api_key': api_key,
            'to': destination,
            'from': senderID,
            'sms': message
        }
        final_url1 = url + "?" + urllib.parse.urlencode(sms_body)
        requests.get(final_url1)

        destination = str(self.receive_phone)
        message = "M./Mme " + self.receive_id.name + "vous venez de retirer votre colis  numero " + str(self.numero_colis) + "Merci de faire confiance a MTCS SARL"
        sms_body = {
            'action': 'send-sms',
            'api_key': api_key,
            'to': destination,
            'from': senderID,
            'sms': message
        }
        final_url2 = url + "?" + urllib.parse.urlencode(sms_body)
        requests.get(final_url2)

        return self.write({'state': 'receive'})


class ville_colis(models.Model):
    """Defining model for ville colis."""
    _description = "Ville d'envoi  des Colis"
    _name = 'ville.envoi.colis'
    _rec_name ='name'

    name = fields.Char("Ville d'envoi")

class ville_colis(models.Model):
    """Defining model for ville colis."""
    _description = "Ville  de reception des Colis"
    _name = 'ville.recept.colis'
    _rec_name ='name'

    name = fields.Char("Ville de reception")


