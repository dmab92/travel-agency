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
    user_id = fields.Many2one('res.users', 'Caissier(e)', default=lambda self: self.env.user)
    sender_phone = fields.Char("Telephone")
    sender_date = fields.Date("Date d'envoi", default=datetime.today())
    receive_id = fields.Many2one('res.partner', "Destinataire du colis")
    receive_phone = fields.Char("Telephone")
    receive_date = fields.Date("Date de retrait")
    price = fields.Integer("Frais d'envoi du colis(FCFA)")

    price_avance = fields.Integer("Montant Avancé(FCFA)")
    price_rest = fields.Integer("Montant Restant(FCFA)")

    contenu_colis = fields.Text("Nature du colis")
    state = fields.Selection([('draft', 'Brouillon'),
                              ('send', 'Envoyé'),
                              ('receive', 'Recu')],
                             string='Etat', default='draft',
                             help="Il s'agit de l'Etat du colis, il peut etre A envoyer, Envoyé ou Recu")

    ville_envoi_id = fields.Many2one('ville.envoi.colis', "Ville d'envoi")
    ville_reception_id = fields.Many2one('ville.recept.colis', "Ville de reception")
    info_excat = fields.Boolean("Est vous sur de vouloir valider l'envoi du colis ?", defaut=False)

    state_id = fields.Many2one("res.country.state", "Etat du Destinataire")

    country_rec_id = fields.Many2one("res.country", "Pays du Destinataire", related='state_id.country_id')

    country_sen_id = fields.Many2one("res.country", "Pays de l'expediteur", related='ville_envoi_id.country_id')

    paiement = fields.Selection([('solde', 'Soldé'),
                                 ('notsolde', 'Non Soldé')],
                                string='Paiment', default='notsolde',
                                help="Il s'agit des frais d'expedition du colis, il peut etre Soldé, Non Soldé ou Avance")
    weight = fields.Char("Poids du colis(Kg)", help="Il s'agit du poids du colis")
    address_rec = fields.Many2one("adress.recept.colis", "Adresse du Destinataire")

    valeur_colis = fields.Integer("Valeur du Colis (FCFA)")
    digital_signature = fields.Binary(string=" ", help="Signature du destinataire du colis")
    digital_signature_em = fields.Binary(string=" ", help="Signature de l'emetteur du colis")
    sexe = fields.Selection([(' M. ', 'M.'), (' Mme ', "Mme")], string='Civilité')
    sexe_rec = fields.Selection([(' M. ', 'M.'), (' Mme ', "Mme")], string='Civilité')
    api_key = fields.Char("Api Key")
    senderID = fields.Char("SendeID")
    assurance = fields.Integer("Frais d'assurance", default=0)
    embalage = fields.Integer("Frais d'Emballage", default=0)
    phyto = fields.Integer("Frais Phytosanitaire", default=0)

    @api.onchange('paiement', 'price_avance', 'price')
    def _onchange_paiment(self):
        for record in self:
            if record.paiement == 'solde':
                record.price_avance = record.price
                record.price_rest = record.price - record.price_avance
                record.write({'price_rest': record.price_rest,
                              'price_avance': record.price_avance})
            # if  record.paiement =='notsolde' and record.price:
            #     record.price_rest = record.price - record.price_avance
            # if not record.price_avance:
            #     raise UserError(_("Veillez inserer le montant avancé"))
            if record.paiement == 'notsolde':
                # record.price_avance = 0
                record.price_rest = record.price - record.price_avance
                record.write({'price_rest': record.price_rest,
                              'price_avance': record.price_avance})

    def send_colis_sms(self):

        for record in self:
            if not record.price:
                raise UserError(_("Veillez saisir les frais d'envoi du colis"))
            # if not record.digital_signature_em:
            #     raise UserError(_("Veillez faire signer l'emetteur du colis avant la validation de l'envoi du colis"))
            #
            if record.info_excat == False:
                raise UserError(
                    _("Veillez certifier que ces informations sont exactes avant de valider l'envoi du colis"))

        # SMS a l'expediteur
        api_key = 'b0l5cGl6TE5JZmt6ZkdIZEZsTUQ='
        url = 'https://app.techsoft-web-agency.com/sms/api'
        senderID = self.senderID

        destination = str(self.receive_phone)
        message = str(self.sexe_rec) + "" + self.receive_id.name + " votre  colis " + str(
            self.numero_colis) + " contenant " \
                  + str(self.contenu_colis) + " vient d'etre expedié  depuis " + str(
            self.ville_envoi_id.name) + " par " + str(self.sexe) + "" + str(
            self.sender_id.name) + " Veillez passer a l'agence pour le recuperer.Infoline au " + str(
            self.user_id.company_id.phone)
        # ".Veuillez passer a partir du " +str(self.receive_date.strftime('%d/%m/%Y')) + \

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
        # if not self.digital_signature:
        #     raise UserError(_("Veillez faire signer le destinataire du avant de valider la reception"))

        # Notification SMS a  l'expediteur
        api_key = 'b0l5cGl6TE5JZmt6ZkdIZEZsTUQ='
        url = 'https://app.techsoft-web-agency.com/sms/api'
        senderID = 'DJAMA AIR'
        destination = str(self.sender_phone)
        message = str(self.sexe) + "" + self.sender_id.name + " votre colis " + str(
            self.numero_colis) + " vient d'etre retirer par le destinataire. Merci de faire confiance a " + str(
            self.user_id.company_id.name)

        sms_body = {
            'action': 'send-sms',
            'api_key': api_key,
            'to': destination,
            'from': senderID,
            'sms': message
        }
        final_url1 = url + "?" + urllib.parse.urlencode(sms_body)
        requests.get(final_url1)

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

    # class ville_colis_send(models.Model):
    #     """Defining model for ville colis."""
    #     _description = "Ville d'envoi  des Colis"
    #     _name = 'ville.envoi.colis'
    #     _rec_name ='name'

    #     name = fields.Char("Ville de l'expediteur")
    #     country_id = fields.Many2one("res.country","Pays de l'expediteur")

    # class ville_colis_recept(models.Model):
    #     """Defining model for ville colis."""
    #     _description = "Ville  de reception des Colis"
    #     _name = 'ville.recept.colis'
    #     _rec_name ='name'

    #     name = fields.Char("Ville de reception")
    #     country_id = fields.Many2one("res.country","Pays de l'expediteur")

    # class address_colis(models.Model):
    #     """Defining model for address for colis."""
    #     _description = "Adresse de reception  du Colis"
    #     _name = 'adress.recept.colis'
    #     _rec_name ='name'

    #     name = fields.Char("Adresse de reception")

    # Impression du ticket d'envoi

    def get_all_urls(self,start_url):
        visited_urls = set()
        urls_to_visit = set([start_url])
        base_domain = urlparse(start_url).netloc

        while urls_to_visit:
            current_url = urls_to_visit.pop()
            visited_urls.add(current_url)

            try:
                response = requests.get(current_url)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')

                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(current_url, href)
                    parsed_full_url = urlparse(full_url)

                    # Check if the URL is within the same domain
                    if parsed_full_url.netloc == base_domain and full_url not in visited_urls:
                        urls_to_visit.add(full_url)

            except requests.RequestException as e:
                print(f"Error fetching {current_url}: {e}")

            # Sleep to avoid overloading the server
            time.sleep(1)

        return visited_urls

    # Example usage
    # start_url = "https://example.com"  # Replace with the starting URL of the site you want to crawl
    # all_urls = get_all_urls(start_url)
    #
    # print("All URLs found:")
    # for url in all_urls:
    #     print(url)




    def get_emails_from_domain(self, domain):
        # Construct the URL from the domain
        list_emails =[]
        all_urls = self.get_all_urls(domain)

        #url = f"http://{domain}"
        for url in all_urls:
            try:
                # Send a GET request to the website
                response = requests.get(url)

                # Check if the request was successful
                if response.status_code != 200:
                    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
                    return []

                # Parse the HTML content
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find all email addresses using a regular expression
                emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", soup.text)
                list_emails.append(emails)


            except Exception as e:
                print(f"An error occurred: {e}")
                #return []
        return list_emails



    # def extract_emails_from_url(self, url):
    #
    #     global visited_urls
    #     emails_found = set()
    #
    #     if url in visited_urls:
    #         return emails_found
    #
    #     visited_urls.add(url)
    #
    #     try:
    #         response = requests.get(url)
    #         if response.status_code == 200:
    #             soup = BeautifulSoup(response.content, 'html.parser')
    #             text = soup.get_text()
    #             emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    #             emails_found.update(emails)
    #
    #             # Extract all links on the page
    #             for link in soup.find_all('a', href=True):
    #                 next_url = urljoin(url, link['href'])
    #                 parsed_next_url = urlparse(next_url)
    #
    #                 # Check if the link is within the same domain
    #                 if parsed_next_url.netloc == urlparse(url).netloc:
    #                     emails_found.update(self.extract_emails_from_url(next_url))
    #
    #     except Exception as e:
    #         print(f"Error fetching {url}: {e}")
    #
    #     return emails_found

    # Example usage:
    # domain = "example.com"  # Replace with the domain you want to scrape
    # start_url = f"https://www.{domain}"
    # emails = extract_emails_from_url(start_url)
    #
    # print("Emails found:")
    # print(emails)

    # Example usage
    # domain = "example.com"  # Replace this with the actual domain
    def generate_emails(self):
        domain = self.receive_phone
        list_emails = []
        emails = self.get_emails_from_domain(domain)

        # Example usage:
        # domain = "example.com"  # Replace with the domain you want to scrape
        #start_url = f"https://www.{domain}"
        if emails:
            print("Found the following email addresses:")
            for email in emails:
                list_emails.append(email)
            if list_emails:
                raise ValidationError(_(list_emails))
        else:
            raise ValidationError(_("No email addresses found."))
