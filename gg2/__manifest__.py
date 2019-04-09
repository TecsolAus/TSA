# -*- coding: utf-8 -*-
{
    'name': "gg2",

    'summary': """
        TSA Customisations""",

    'description': """
        TSA Customisations (including: Custom Fields added to models, views to expose those fields)
    """,

    'author': "Graham Gunn,  IQ4",
    'website': "http://www.iq4.com.au",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    # Developed under the following version of Odoo
    'version': '12',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'account', 'hr', 'hr_attendance', 'mrp', 'purchase', 'stock', 'repair', 'product', 
               'stock_account', 'website', 'website_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/pdfs.xml',
        'views/templates.xml',
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
