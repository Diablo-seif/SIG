# pylint: disable=skip-file
{
    'name': 'SIG Applicant',
    'summary': 'SIG Applicant',
    'author': "Mohamed Osama, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'sequence': 1,
    'depends': [
        'base',
        'hr_recruitment',
        'sig_contact',
    ],
    'data': [
        'security/security.xml',
        'views/res_partner.xml',
        'views/hr_applicant.xml',
        'views/hr_employee.xml',
        'views/recruitment_menu.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
