# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import ValidationError,UserError
import time

class voyage_voyage(models.Model):
    """Defining model for voyage."""
    _name = 'voyage.voyage'
    _description = 'voyage'
    _rec_name = 'name'
    _order = 'id DESC'

    def _get_next_reference(self):
        query = """SELECT COUNT(id) AS ligne FROM voyage_voyage"""
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


    date_register = fields.Datetime('Date et Heure de depart', default=fields.datetime.now())
    name = fields.Char("Numero du Voyage",readonly="True", default = lambda self: self._get_next_reference())
    user_id = fields.Many2one("res.users", "Guichetier(e)", default=lambda self: self.env.user, required=1)
    car_id = fields.Many2one("fleet.vehicle", "Vehicule",required=1)
    driver_id = fields.Many2one("res.partner", "Conducteur",required=1)
    #line_ids = fields.One2many('voyage.passager','voayge_id', string="Passagers")
    line_ids = fields.One2many('lines.voyage', 'voayge_id', string="Passagers")

    state = fields.Selection([('draft', 'Brouillon'),
                              ('send', 'Validé'),
                              ('cancel', 'Annulé'),
                              ], require=1, default='draft',
                             string='Etat')
    letter = fields.Char("Lettre du Bus")

    total_bagage = fields.Integer("Total Bagages", compute='_compute_passanger_number')
    total_frais = fields.Integer("Total de Transport",compute='_compute_passanger_number',digits=0)
    total_remb = fields.Integer("Total Remboursement",compute='_compute_passanger_number',digits=0)
    total_gain = fields.Integer("Total Gain", compute='_compute_passanger_number',digits=0)
    road_fees= fields.Integer("Frais de route", digits=0)
    departure_id = fields.Many2one("ville.envoi.colis", " Depart")
    destination_id = fields.Many2one("ville.recept.colis","Destination")
    type_id = fields.Many2one("voyage.type", "Type")
    price = fields.Integer("Frais de transport",  related='type_id.price', digits=(6,0))
    license_plate = fields.Integer("Frais de route")
    passenger_number = fields.Integer("Nombre max de passagers", related='car_id.seats')

    confirm = fields.Boolean("Je confirme avoir reelu cette fiche et n'avoir apercu aucune anomalie")



    @api.onchange('line_ids')
    def _compute_passanger_number(self):
        """Compute the invoice count"""
        for record in self:
            #record.passenger_number = len(record.line_ids)
            record.total_frais = sum(record.line_ids.mapped('price'))
            record.total_bagage = sum(record.line_ids.mapped('price_bagage'))
            record.total_remb =sum(record.line_ids.mapped('rembour'))
            record.total_gain= record.total_frais + record.total_bagage - record.total_remb

    @api.constrains('line_ids')
    def _check_control_date(self):
        for line in self:
            if len(line.line_ids) > line.passenger_number:
                raise UserError(_(" Impossible d'enregistrer car le bus est deja plein. NB: la capacité maximale de ce"
                                  " vehicule est de  %s  personnes. Veillez supprimer le(s) %s derniers "
                                  "passager(s) que vous avvez ajouter et le(s) programmer si possible au prochain depart. ") %(line.car_id.seats, (len(line.line_ids) - line.passenger_number)))
        return True

    @api.onchange('price')
    def _onchange_price(self):
        "On change the price of transfort"
        for record in self:
            record.line_ids.price = record.price


    @api.onchange('car_id')
    def _onchange_car_id(self):
        for record in self:
            record.road_fees = record.car_id.horsepower_tax
            record.license_plate = record.car_id.license_plate
            record.driver_id = record.car_id.driver_id
            #record.write({'road_fees': record.price_rest,
                          #'license_plate': record.price_avance})

    @api.onchange('car_id')
    def _onchange_car_id(self):
        for record in self:
            record.road_fees = record.car_id.horsepower_tax
            record.license_plate = record.car_id.license_plate
            record.driver_id = record.car_id.driver_id

    def print_bordeau(self):

        return self.env.ref('travel_agency_app.action_report_bordeau').report_action(self)
    def set_valited(self):
        "Check de nomber of line "
        if len(self.line_ids) == 0 :
            raise UserError(_("'Alert !!! Veuillez inserer au moins un passager avant de valider ce voyage '"))

        if not self.confirm :
            raise UserError(_("'Alert !!! Veuillez  confirmer l'exactude des ces informations avant de les valider'"))

        return self.write({'state': 'send'})

    def set_draft(self):
        return self.write({'state':'draft'})

    def set_cancel(self):
        return self.write({'state': 'cancel'})

class voyage_passager(models.Model):
    """Defining the passengers ."""
    _description = 'Passagers'
    _name = 'voyage.passager'
    _rec_name = 'mobile'


    partner_id = fields.Many2one('res.partner' , "Noms et Prenoms", required=1)
    cni = fields.Char("CNI")
    mobile = fields.Char("Tel:")

    #voayge_id = fields.Many2one("voyage.voyage", "Voyage")
    #price = fields.Integer("Frais de Transport", related='voayge_id.price')
    #price_bagage = fields.Integer("Prix Bagage")
    #bagage = fields.Char("Bagages")
    #rembour = fields.Integer("Remboursement")
    #sexe = fields.Selection([(' M. ', 'Homme'), (' Mme ', "Femme")], string='Civilité')

    #user_id = fields.Many2one("res.users", "Guichetier(e)", default=lambda self: self.env.user, readonly="1")

    #siege_number = fields.Integer(string="Sequence", compute="_compute_sequence", store=True)

    # @api.depends('voayge_id.line_ids')
    # def _compute_sequence(self):
    #     for record in self:
    #         if record.voayge_id:
    #             # Iterate through the One2many field and assign the sequence number
    #             for index, line in enumerate(record.voayge_id.line_ids, start=1):
    #                 line.siege_number = index

    # @api.onchange('partner_id')
    # def _onc_siege_number(self):
    #     for record in self:
    #         record.siege_number += 1

    # def print_ticket(self):
    #      return self.env.ref('travel_agency_app.action_report_ticket').report_action(self)

class voyage_line(models.Model):
    """Defining the passengers ."""
    _description = 'Les lignes de voyages'
    _name = 'lines.voyage'
    _rec_name = 'numero_id'

    numero_id = fields.Many2one('voyage.passager', "Tel:")
    mobile = fields.Char(related='numero_id.mobile', string='Mobile', store=True)
    partner_id = fields.Many2one('res.partner', "Noms et Prenoms")
    cni = fields.Char("Numero de CNI")
    price = fields.Integer("Frais de Transport", related='voayge_id.price')
    price_bagage = fields.Integer("Prix Bagage")
    rembour = fields.Integer("Remboursement")
    bagage = fields.Char("Bagages")
    voayge_id = fields.Many2one("voyage.voyage", "Voyage")
    user_id = fields.Many2one("res.users", "Guichetier(e)", default=lambda self: self.env.user)

    siege_number = fields.Integer(string="Sequence", compute="_compute_sequence", store=True)


    @api.depends('voayge_id.line_ids')
    def _compute_sequence(self):
        for record in self:
            if record.voayge_id:
                # Iterate through the One2many field and assign the sequence number
                for index, line in enumerate(record.voayge_id.line_ids, start=1):
                    line.siege_number = index

    @api.onchange('numero_id')
    def _onc_siege_number(self):
        for record in self:
            record.siege_number += 1

    def print_ticket(self):
         return self.env.ref('travel_agency_app.action_report_ticket').report_action(self)


    @api.onchange('numero_id')
    def _onchange_mobile(self):
        for record in self:
            record.cni = record.numero_id.cni
            record.partner_id = record.numero_id.partner_id.id


class city_destination(models.Model):
    """Defining  for destinatation."""
    _description = ' Ville de Destination'
    _name = 'city.destination'

    name= fields.Char("Destination")

class city_depart(models.Model):
    """Defining   the city of departure of car."""
    _description = "Vlle d'arrivee"
    _name = 'city.depart'

    name= fields.Char("Arrivee")


class voyage_type(models.Model):
    """Defining   the city of departure of car."""
    _description = " Type de voyage"
    _name = 'voyage.type'

    name= fields.Char("Type")
    price =fields.Integer("Prix")


