# pylint: skip-file
{
    'name': 'Progress Bar Option',
    'summary': 'Progress Bar Option',
    'author': 'Muhamed Abd El-Rhman',
    'maintainer': 'Muhamed Abd El-Rhman',
    'category': 'Tools',
    # 'version': '1.0.0',
    'license': 'OPL-1',
    'depends': [
        'web',
    ],
    'assets': {
        'web.assets_backend': [
            'progress_bar/static/src/**/*',

        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
