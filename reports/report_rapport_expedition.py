# -*- coding:Utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class rapoort_expedition_parser(models.AbstractModel):
    _name = 'report.travel_agency_app.rapport_expedition'
    _description = 'Rapport  des expeditions des colis'


    def _get_report_values(self, docids, data=None):
        domain = [('state', 'in', ['send','receive'])]

        if data.get('date_start'):
            domain.append(('sender_date', '>=', data.get('date_start')))
        if data.get('date_end'):
            domain.append(('sender_date', '<=', data.get('date_end')))
        if data.get('ville_envoi_ids'):
            domain.append(('ville_envoi_id', 'in', data.get('ville_envoi_ids')))
        
        if data.get('ville_reception_ids'):
            domain.append(('ville_reception_id', 'in', data.get('ville_reception_ids')))
        
        # if data.get('souscript_ids'):
        #     domain.append(('souscript_id', 'in', data.get('souscript_ids')))

        # if data.get('mode_payement'):
        #     domain.append(('mode_payement', '=', data.get('mode_payement')))

        docs = self.env['voyage.colis'].search(domain, order="sender_date desc")

        #company_ids = self.env['res.company'].browse(data.get('company_ids'))

        ville_reception_ids = self.env['ville.recept.colis'].browse(data.get('ville_reception_ids'))

        ville_envoi_ids = self.env['ville.envoi.colis'].browse(data.get('ville_envoi_ids'))
        
        data.update({'ville_envoi_ids': ",".join([vil.name for vil in ville_envoi_ids])})

        data.update({'ville_reception_ids': ",".join([vil.name for vil in ville_reception_ids])})

        return {
            'doc_ids': docs.ids,
            'doc_model': 'voyage.colis',
            'docs': docs,
            'datas': data,
            'ville_reception_ids':ville_reception_ids,
            'ville_envoi_ids':ville_envoi_ids
            
        }

    