# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _

class ville_colis_send(models.Model):
    """Defining model for ville colis."""
    _description = "Ville d'envoi  des Colis"
    _name = 'ville.envoi.colis'
    _rec_name ='name'

    name = fields.Char("Ville")
    phone = fields.Char("Numero Agence")


class ville_colis_recept(models.Model):
    """Defining model for ville colis."""
    _description = "Ville  de reception des Colis"
    _name = 'ville.recept.colis'
    _rec_name ='name'

    name = fields.Char("Ville")
    phone = fields.Char("Numero Agence")

class address_colis(models.Model):
    """Defining model for address for colis."""
    _description = "Adresse de reception  du Colis"
    _name = 'adress.recept.colis'
    _rec_name ='name'

    name = fields.Char("Adresse de reception")

