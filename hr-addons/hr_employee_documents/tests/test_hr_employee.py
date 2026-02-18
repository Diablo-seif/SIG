"""Integrated Tests for hr employee"""

from dateutil.relativedelta import relativedelta

from odoo import fields

from odoo.tests.common import TransactionCase


class TestHrEmployee(TransactionCase):
    """ Unit test for object hr employee """

    # pylint: disable=protected-access
    def test_default_get(self):
        """
            test Scenario:
            -   test create hr employee to check default documents
            -   test Expired documents will create activity
        """
        group_hr_user = self.env.ref('hr.group_hr_user')
        hr_employee = self.env.ref('base.user_demo')
        hr_employee.groups_id = [(4, group_hr_user.id)]
        emp_object = self.env['hr.employee'].with_user(hr_employee)
        employee = emp_object.create({'name': 'Employee Test'})
        self.assertTrue(employee.document_line_ids)
        doc = self.env['hr.employee.documents.lines'].create({
            'employee_id': employee.id,
            'document_id': self.env.ref(
                'hr_employee_documents.national_id_employee_document').id,
            'has_expiration': True,
            'expiry_date': fields.date.today() + relativedelta(days=+30),
        })
        domain = doc._onchange_employee_id()
        self.assertEqual(
            domain['domain'], {
                'document_id': [(
                    'id', 'not in', doc.employee_id.mapped(
                        'document_line_ids.document_id'
                    ).ids
                )]
            }
        )
        self.env['hr.employee'].activity_expiry()
        self.assertTrue(employee.activity_ids)
        self.assertEqual(
            employee.activity_ids.mapped('summary')[0],
            '%s will be expired by %s' % (
                doc.document_id.name, doc.expiry_date
            )
        )
