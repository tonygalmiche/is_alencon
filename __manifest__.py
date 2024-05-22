# -*- coding: utf-8 -*-
{
    "name"     : "Module Odoo 16 pour Alençon",
    "version"  : "0.1",
    "author"   : "InfoSaône",
    "category" : "InfoSaône",
    "description": """
Module Odoo 16 pour Alençon
===================================================
""",
    "maintainer" : "InfoSaône",
    "website"    : "http://www.infosaone.com",
    "depends"    : [
        "base",
        "is_plastigray16",
    ],
    "data" : [
        "views/is_theia_view.xml",
        "views/menu.xml",
    ], 
    "qweb": [
    ],
    "assets": {
        'web.assets_backend': [
            'is_alencon/static/src/**/*',
         ],
    },
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}