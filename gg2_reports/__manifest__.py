# -*- coding: utf-8 -*-
{
    'name': "gg2_reports",

    'summary': """
        TSA Customisations - reports""",

    'description': """
        TSA Customisations - reports
    """,

    'author': "Graham Gunn,  IQ4",
    'website': "http://www.iq4.com.au",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    # Developed under the following version of Odoo
    'version': '14.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'account', 'product', 'gg2_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'images': [],
    "images":['static/description/Banner.png'],
}
