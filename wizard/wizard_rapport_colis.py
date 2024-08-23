# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
class wizard_stock_bordereau(models.TransientModel):
    _name = 'wizard.travel.expedit'
    _description ='Borderau d''expedition des colis'


    date_start = fields.Datetime('Date de debut', index=True, required=True)
    date_end = fields.Datetime('Date de fin', index=True, required=True)
    ville_envoi_ids = fields.Many2many('ville.envoi.colis', string="Ville d'envoi")
    ville_reception_ids = fields.Many2many('ville.recept.colis', string="Ville de reception")


    def print_rapport(self):
        if self.date_start >= self.date_end:
            raise UserError(_("Erreur !!!! La date de debut ne peut pas etre plus recente que la date de fin"))

        datas = {
            'date_start': self.date_start,
            'date_end': self.date_end,
            'ville_envoi_ids':self.ville_envoi_ids.ids,
            'ville_reception_ids':self.ville_reception_ids.ids,
        }
        
        return self.env.ref('travel_agency_app.action_report_rapport_colis').report_action(self, data=datas)




        