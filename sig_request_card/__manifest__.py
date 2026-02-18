{
    'name': 'SIG Request Card',
    # 'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Module for managing employee request cards',
    'author': 'CORE B.P.O',
    'depends': ['hr'],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'report/report.xml',
        'report/request_card_report.xml',
        'views/associated_company_views.xml',
        'views/job_position_views.xml',
        'views/job_grade_views.xml',
        'views/request_card_governorate_views.xml',
        'views/request_card_views.xml',
        'views/request_card_template.xml',
        'views/menu_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
