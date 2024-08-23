# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import fields, models, api,exceptions
from odoo.exceptions import UserError, Warning, ValidationError
import base64
import codecs, io
import xlwt

class wizard_colis_report(models.TransientModel):

    _name = "agency.wizard.coli.report"
    _description = "wizard Caisse des colis"

    date_start = fields.Datetime('Date de debut', index=True, required=True)
    date_end = fields.Datetime('Date de fin', index=True, required=True)
    ville_envoi_ids = fields.Many2many('ville.envoi.colis', string="Ville d'envoi")
    ville_reception_ids = fields.Many2many('ville.recept.colis', string="Ville d'expedition")


    state = fields.Selection([('draft', 'Brouillon'),
                              ('send', 'Envoyé'),
                              ('receive', 'Recu')],
                             string='Etat', default='send',
                             help="Il s'agit de l'Etat du colis, il peut etre A envoyer, Envoyé ou Recu")

    paiement = fields.Selection([('solde', 'Soldé'),
                              ('notsolde', 'Non Soldé')],
                             string='Paiment', default='notsolde',
                             help="Il s'agit des frais d'expedition du colis, il peut etre Soldé, Non Soldé ou Avance")
    

    file_name = fields.Char('Nom du fichier', size=255, readonly=True)
    file_data = fields.Binary('File', readonly=True)
    bool = fields.Boolean('Exporté', readonly=True)


    def date_to_literal(self, date):
        month_to_literal = [
            'Janvier',
            'Fevrier',
            'Mars',
            'Avril',
            'Mai',
            'Juin',
            'Juillet',
            'Aout',
            'Septembre',
            'Octobre',
            'Novembre',
            'Decembre',
        ]
        ##        print date
        if isinstance(date, str):
            if len(date) == 10:
                format = '%Y-%m-%d'
            else:
                format = '%Y-%m-%d %H:%M:%S'
        date = datetime.strptime(date, format)

        if not isinstance(date, datetime):
            return ''
        return str(date.day).zfill(2) + ' ' + month_to_literal[date.month - 1] + ' ' + str(date.year)

    @api.constrains('date_debut', 'date_fin')
    def _check_control_date(self):
        for line in self:
            if line.date_fin < line.date_debut:
                raise Warning("La date de début doit être inférieur à la date de fin ")
        return True

    
    def print_report(self):
        for elt in self:
                data = self._get_colis_data(self.date_debut, self.date_fin)
                #print (data)
                buf = io.StringIO.StringIO()
                buffer_xls = io.StringIO.StringIO()
                wb = xlwt.Workbook(encoding='cp1251')
                ws = wb.add_sheet(u'ETATS DES COLIS')
                style_number = xlwt.easyxf('font: name Times New Roman', num_format_str='#,##0')
                # ------------------- Corps du fichier --------------------#

                for i in range(len(data)):
                    for j in range(len(data[i])):
                        if j < len(data[i]):
                            ws.write(i, j, data[i][j], style_number)
                wb.save(buffer_xls)
                file = base64.encodestring(buffer_xls.getvalue())
                buffer_xls.close()
                buf.close()
                fname = u'Etat Statistique des colis.xls'
                self.write({'file_data': file, 'file_name': fname, 'bool': True})
                return {
                    'name': 'Exportation des fichiers',
                    'type': 'ir.actions.act_window',
                    'res_model': 'travel_agency_app.wizard.colis.report',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id': elt.id,
                    'views': [(False, 'form')],
                    'target': 'new',
                }


    @api.model
    def _get_colis_data(self, date_start, date_end, ville_envoi_ids,ville_reception_ids):

        colis_obj = self.env.get('voyage.colis')
        #speciality_obj = self.env.get('hr.specialite')
        total_amount = 0.0;
        # 

        data = [
            [u' ETATS STATISTIQUES DES COLIS D\'EMPLOI DU ' + self.date_to_literal(date_start) + ' AU '+ self.date_to_literal(date_end)],
            [' '],
            [u' ', u"Numero ", u"Date d'envoi", u"Expediteur",u"Ville d'envoi", u"Frais d'envoi", u"Etat du Paiment"]
        ]

        if self.ville_envoi_ids :
            colis_ids = colis_obj.search([('sender_date', '>=', date_start), 
                ('sender_date', '<=', date_end), 
                ('state', 'in', ['send','receive']),
                ('ville_envoi_id', 'in', ville_envoi_ids.ids), 
                ])
        if self.ville_reception_ids :
            colis_ids = colis_obj.search([('sender_date', '>=', date_start), 
                ('sender_date', '<=', date_end), 
                ('state', 'in', ['send','receive']),
                ('ville_reception_id', 'in', ville_reception_ids.ids), 
                ])
        else:
            colis_ids = colis_obj.search([])

        len_total = len(colis_ids)
        indis = 0
        for colis in colis_ids:
            total_amount = total_amount + colis.price
            indis += 1
            data.append([indis,colis.numero_colis,colis.sender_date,colis.ville_envoi_id.name,colis.price,colis.paiement])

        data.append([''])
        if len_total != 0:
            data.append(['Nombre Total des colis envoyé', len_total ] )
            data.append(['Montant TOTAL', total_amount])
            
        data.append([''])
        return data



# from odoo import api, fields, models, _
# from odoo.exceptions import UserError


# class wizard_rapport_colis(models.TransientModel):
#     _name = 'wizard.travel_agency_app.rapport.colis'
#     _description = 'Rapport  des colis'

#     date_start = fields.Datetime('Date de debut', index=True, required=True)
#     date_end = fields.Datetime('Date de fin', index=True, required=True)
#     ville_envoi_ids = fields.Many2many('ville.envoi.colis', string="Ville d'envoi")
#     ville_reception_ids = fields.Many2many('ville.recept.colis', string="Ville d'expedition")

#     def print_rapport(self):
#         if self.date_start >= self.date_end:
#             raise UserError(_("Erreur !!!! La date de debut ne peut pas etre plus recente que la date de fin"))
     
#         datas={ 'date_start': self.date_start,
#                 'date_end': self.date_end,
#                 'ville_envoi_ids': self.ville_envoi_ids.ids,
#                 'ville_reception_ids': self.ville_reception_ids.ids}

#         return self.env.ref('travel_agency_app.action_report_rapport_colis').report_action(self, data=datas)




