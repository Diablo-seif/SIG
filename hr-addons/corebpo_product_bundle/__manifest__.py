{
    "name": "CORE Product Bundle",
    'author': "Mohamed Osama, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'Extra Tools',
    # 'version': '1.0.0',
    'license': 'AGPL-3',
    "depends": [
        "sh_base_bundle",
        "sale_management",
        "purchase",
        "proposal",
    ],
    "data": [
        "views/sale_order.xml",
        "views/purchase_order.xml",
        "views/proposal.xml",
    ],
    "application": True,
    "auto_install": False,
    "installable": True,
}
