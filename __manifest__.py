# -*- coding: utf-8 -*-
{
    'name': "Travel Agency Managment System",

    'summary': """
       Ce module vous permet de gerer l'enseignment des activites d'une agence de transport interurbain
       """,

    'description': """
         Ce module vous permet de gerer l'enseignment des activites d'une agence de transport
       de l'enregistremnt des voyages, les badages, l'impression des tickets, des bordeau de route et bien d'autres elements
        d'Editer vos etats Statistiques aux format PDF et Excel
    """,
    'author': "MT Consulting  SARL",
    'email': "contact@mtconsulting.cm",
    'website': "http://www.mtconsulting.cm",
    'phone': "+237 678128120 /697005649",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','fleet'],

    # always loaded
    'data': [
        #'security/groups.xml'
        'data/layouts.xml',
        'security/ir.model.access.csv',

        'views/colis_views.xml',
        'views/colis_config.xml',
        'views/voyages.xml',
        'views/transport.xml',
        'views/pieces.xml',
        #'views/sales_dashboard.xml',
        'views/location.xml',
        'views/bordeau_views.xml',
        'wizard/wizard_rapport_colis.xml',
        'reports/report_ticket_expedition.xml',
        'reports/report_rapport_expedition.xml',
        'reports/report_borderau.xml',
         'reports/report_borderau_colis.xml',
        'reports/report_ticket_bus.xml',
        'report_voyage.xml',
        'menu_voyage.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
       # 'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,

'assets': {
    'web.assets_backend': [

        #'travel_agency_app/static/src/components/**/*.js',
        #'travel_agency_app/static/src/components  /**/*.xml',
         #'travel_agency_app/static/src/components/**/*.scss',
       # 'travel_agency_app/static/src/css/custom_styles.css',

    ],
},
}
