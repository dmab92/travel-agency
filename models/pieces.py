# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError,ValidationError

import time

class pieces_dossier_v(models.Model):
    """Defining les pieces de dossiers d'un vehicule."""
    _name = 'dossier.vehicule'
    _description = 'Dossiers Vehicules'
    _rec_name = 'name'
    _order = 'id DESC'

    name = fields.Char("Nom de la  Piece")
    date_emi = fields.Date("Date d'Emission")
    date_expi = fields.Date("Date d'Expritaion")
    validity = fields.Char("Durée de Validité(en Années)")

    state = fields.Selection([('valid', 'Valide'),
                              ('unvalid', 'Non Valide')], default='valid', string='Etat')

    vehicule_id = fields.Many2one('vehicule.voyage')



class pieces_dossier_d(models.Model):
    """Defining les pieces de dossiers d'un vehicule."""
    _name = 'dossier.chauffeur'
    _description = 'Dossiers Chaffeurs'
    _rec_name = 'name'
    _order = 'id DESC'

    name = fields.Char("Nom de la  Piece")
    validity = fields.Char("Durée de Validité(en Années)")
    date_emi = fields.Date("Date d'Emission")
    date_expi = fields.Date("Date d'Expritaion")

    state = fields.Selection([('valid', 'Valide'),
                              ('unvalid', 'Non Valide')], default='valid', string='Etat')

    driver_id = fields.Many2one('driver.voyage')





