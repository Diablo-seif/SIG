# pylint: skip-file
{
    'name': "FontAwesome Icon Selector",
    'summary': "Icon Chooser Widget",
    'author': 'Anass Ahmed, CORE B.P.O',
    # 'version': '1.0.0',
    'category': 'Web',
    'license': 'AGPL-3',
    'depends': [
        'web',
    ],
    'data': [
    ],
    'assets': {
        'web.assets_backend': [
            '/web_icon_selector/static/src/js/icon_selector.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
