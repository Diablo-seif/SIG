# pylint: disable=missing-docstring,manifest-required-author
{
    'name': 'HR Organization Chart',
    'summary': 'HR Organization Chart',
    'author': "Muhamed Abd El-Rhman, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    # 'version': '13.0.1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'depends': ['hr', 'web', 'hr_job_position'],
    'data': [
        'views/hr_employee.xml',
    ],
    'qweb': [
        'static/src/xml/chart.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'assets': {
        'web.assets_backend': [
            'hr_organization_chart/static/src/css/chart_style.css',
            'hr_organization_chart/static/src/js/libs/d3.v3.min.js',
            'hr_organization_chart/static/src/js/libs/d3-funnel.js',
            'hr_organization_chart/static/src/js/org_chart_view.js',
            'hr_organization_chart/static/src/js/org_chart_model.js',
            'hr_organization_chart/static/src/js/org_chart_controller.js',
            'hr_organization_chart/static/src/js/org_chart_render.js',
        ],
    }
}
