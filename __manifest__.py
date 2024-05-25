# -*- coding: utf-8 -*-
{
    'name': "colis_app",

    'summary': """
       Ce module vous permet de gerer les livraisions de vos colis""",

    'description': """
        Ce module vous permet de gerer les livraisions de vos colis
        Envoyer les SMS a l'Expediteur et  au Destinataire
        d'Editer vos etats Statistiques aux format PDF et Excel
    """,
    'author': "MT Consulting and Services",
    'email': "contact@mtconsultingandservices.com",
    'website': "http://www.mtconsultingandservices.com",
    'phone': "+237 678128120 /697005649",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','fleet'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'data/layouts.xml',
        'views/colis_views.xml',
        'views/colis_config.xml',
        'views/voyage.xml',
        'wizard/wizard_rapport_colis.xml',
        'reports/report_ticket_expedition.xml',
        'reports/report_rapport_expedition.xml',
        'reports/report_borderau.xml',
        'reports/report_ticket_bus.xml',
        'report_colis.xml',
        'menu_voyage.xml',

        #'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
       # 'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
