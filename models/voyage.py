# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
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


    date_register = fields.Datetime('Date et Heure de depart', default=fields.datetime.now())
    name = fields.Char("Numero du Voyage",readonly="True",default = lambda self: self._get_next_reference())
    user_id = fields.Many2one("res.users", "Caissiere", default=lambda self: self.env.user)
    car_id = fields.Many2one("fleet.vehicle", "Vehicule")
    driver_id = fields.Many2one("res.partner", "Conducteur")
    passager_ids = fields.One2many('voyage.passager','voayge_id', string="Passagers")

    depart = fields.Selection([('1', 'DOUALA'),
                               ('2', 'NKONGSAMBA'),
                               ],
                             string='Depart')
    state = fields.Selection( [('draft', 'brouillon'),
                               ('send', 'Valider')], string='Etat')
    total_bagage = fields.Char("Total Bagages")
    total_frais = fields.Char("Total de Transport")
    road_fees= fields.Char("Frais de route")
    departure_id = fields.Many2one("city.destination", " Depart")
    destination_id = fields.Many2one("city.depart","Destination")

    road_fees = fields.Integer("Frais de route")
    license_plate = fields.Integer("Frais de route")
    passenger_number = fields.Integer("Nombre max de passagers", related='car_id.seats')

    def _compute_passanger_number(self):
        """Compute the invoice count"""
        for record in self:
            record.passenger_number = len(record.passager_ids)

    @api.constrains('passager_ids')
    def _check_control_date(self):
        for line in self:
            if len(line.passager_ids) > line.passenger_number:
                raise Warning(" Impossible d'enregistrer car vous avez enregistrer plus de passagers que la normale."
                              "NB: la capacité maximale de ce vehicule est de  %s  personnes ") %str(line.car_id.seats)
        return True



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
        return self.env.ref('colis_app.action_report_bordeau').report_action(self)
    def line_check(self):
        "Check de nomber of line "
        pass


class passager_voyage(models.Model):
    """Defining the passengers ."""
    _description = 'Passagers'
    _name = 'voyage.passager'

    partner_id = fields.Many2one('res.partner' , "Noms et Prenoms")
    cni = fields.Char("Numero de CNI")
    mobile = fields.Char("Tel:")
    voayge_id = fields.Many2one("voyage.voyage", "Voyage")
    price = fields.Char("Frais de Transport")
    price_bagage = fields.Char("Prix Bagage")
    remboursement = fields.Char("Remboursement")
    sexe = fields.Selection([(' M. ', 'Homme'), (' Mme ', "Femme")], string='Civilité')


    def print_ticket(self):
         return self.env.ref('colis_app.action_report_ticket').report_action(self)
class city_destination(models.Model):
    """Defining  for destinatation."""
    _description = ' Ville de Destination'
    _name = 'city.destination'

    name= fields.Char("Destination")

class city_departure(models.Model):
    """Defining   the city of departure of car."""
    _description = "Vlle d'arrivee"
    _name = 'city.depart'

    name= fields.Char("Arrivee")




