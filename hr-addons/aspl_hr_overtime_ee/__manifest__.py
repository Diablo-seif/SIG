# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
{
    'name' : 'HR Overtime (Enterprise)',
    # 'version' : '1.0',
    'summary': 'HR Overtime',
    'author' : 'Acespritech Solutions Pvt. Ltd.',
    'category' : 'Human Resources',
    'website' : 'http://www.acespritech.com',
    'description': """
    """,
    'price': 25,
    'currency': 'EUR',
    'depends' : ['hr_payroll', 'hr_attendance'],
    'images': ['static/description/main_screenshot.png'],
    'data': [
            'security/security_view.xml',
            'security/ir.model.access.csv',
            'data/overtime_schedular.xml',
            'data/hr_employee_overtime_data.xml',
            # 'data/payroll_data.xml',
            'views/hr_employee_views.xml',
            'views/res_config_views.xml',
            'views/hr_employee_overtime_views.xml',
            'views/hr_payslip_views.xml',
            
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
