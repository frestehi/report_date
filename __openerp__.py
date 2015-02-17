# -*- coding: utf-8 -*-
{
    'name': "CRM-Report Date Itatel",

    'summary': """Reportes y ajustes Itatel""",

    'author': "PeruSWFactory",
    'website': "http://www.peruswfactory.com",

    'category': 'CRM',
    'version': '0.1',

    'depends': ['crm',
                'crm_extension',
                'sale'],

    'data': [
        'view/ajust_month_line_view.xml',        
        'view/report_date_view.xml',
        'view/crm_photo_view.xml',
        #'view/crm_ajust_line_view.xml',
        'view/cmr_ajust_month_view.xml',
        #'view/crm_ajust_mes_view.xml',
        'security/ir.model.access.csv',
    ],

    'demo': [
        #'demo/_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
}
