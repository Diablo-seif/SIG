# pylint: disable=skip-file
{
    'name': 'HR Applicant ',
    'summary': 'HR Applicant Test',
    'author': "Mohamed Osama, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'sequence': 1,
    'depends': [
        'base',
        'hr_recruitment',
    ],
    'data': [
        'views/hr_applicant.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
