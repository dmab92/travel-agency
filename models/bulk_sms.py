# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
import time, random
import datetime
import urllib, requests
from datetime import datetime
from odoo.exceptions import UserError, Warning, ValidationError

class bulk_sms(models.Model):
    """Defining model for radio camando."""
    _description = 'Campagne de SMS en masse'
    _name = 'bulk.sms'
    _rec_name ='name'
    _order = 'id DESC'

    
    name = fields.Char("Objet")
    date_register = fields.Datetime('Date', default=fields.datetime.now())
    message = fields.Text("Message")
    company_ids = fields.Many2many('res.company', string="Sociétes/ Entités")
    partner_ids = fields.Many2many('res.partner', string="Personnes a toucher")
    photo = fields.Binary(string="Image à Envoyer")

    state = fields.Selection([('draft', 'A Envoyer'),('send', 'Envoyé')],
                             string='Etat', default='draft',
                             help="Il s'agit de l'Etat des SMS, il peuvent etre en brouillon(en attente d'envoi) ou alors Envoyé")

    
    # @api.onchange('paiement','price_avance','price')
    # def _onchange_paiment(self):
    #     for record in self:
    #         if  record.paiement =='solde':
    #             record.price_avance = record.price
    #             record.price_rest = record.price - record.price_avance
    #             record.write({'price_rest': record.price_rest,
    #                           'price_avance':record.price_avance})
    #         # if  record.paiement =='notsolde' and record.price:
    #         #     record.price_rest = record.price - record.price_avance
    #             # if not record.price_avance:
    #             #     raise UserError(_("Veillez inserer le montant avancé"))
    #         if  record.paiement =='notsolde':
    #             #record.price_avance = 0
    #             record.price_rest = record.price - record.price_avance
    #             record.write({'price_rest': record.price_rest,
    #                           'price_avance':record.price_avance})

    def load_numers(self):
        if not self.company_ids:
            clients_ids = self.env['res.partner'].search([])
        else: 
            clients_ids = self.env['res.partner'].search([('company_id', 'in', self.company_ids.ids)])

        for record in self:
                #record.payment_ids = False
                for client in clients_ids:
                    if not client.mobile :
                        pass
                    else:
                        vals = {
                             'name': client.name,
                             'mobile': client.mobile,
                             'company_id': client.company_id and client.company_id.id, 
                             
                          }
                        record.write({'partner_ids': [[0, 0, vals]]})



    def send_sms(self):
         #SMS a l'expediteur
        api_key='b0l5cGl6TE5JZmt6ZkdIZEZsTUQ='
        url = 'https://app.techsoft-web-agency.com/sms/api'
        #senderID = 'TESTE-DEMO'
        senderID='SOACAM'
        for record in self:
            for partner in record.partner_ids:
                destination = str(partner.mobile)
                message = "M./Mme " + partner.name + " " + str(record.message)
                sms_body = {
                    'action': 'send-sms',
                    'api_key': api_key,
                    'to': destination,
                    'from': senderID,
                    'sms': message
                }
                final_url1 = url + "?" + urllib.parse.urlencode(sms_body)
                requests.get(final_url1)
        return self.write({'state': 'send'})
