# -*- coding: utf-8 -*-
{
    'name': "colis_app",

    'summary': """
       Ce module vous permet de gerer les livraisions de vos colis""",

    'description': """
        Ce module vous permet de gerer les livraisions de vos colis
        Envoyer les SMS a l'Expediteur et  au Destinataire
    """,

    'author': "MB Consulting and Service",
    'website': "http://www.mbconsultingandservices.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/colis_views.xml',
        'menu_colis.xml',
        #'views/views.xml',
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
