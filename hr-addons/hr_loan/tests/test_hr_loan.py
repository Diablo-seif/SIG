"""Integrated Tests for object hr.loan"""
from odoo import tools
from odoo.exceptions import UserError
from odoo.modules.module import get_resource_path
from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase


# pylint: disable=too-many-instance-attributes,too-many-statements
# pylint: disable=no-member,too-many-ancestors,protected-access
@tagged('post_install', '-at_install')
class TestHrLoan(TransactionCase):
    """Integrated Tests"""

    def setUp(self):
        """Setup the testing environment."""
        super(TestHrLoan, self).setUp()
        tools.convert_file(
            self.cr, 'hr_loan', get_resource_path(
                'hr_loan', 'test', 'account_minimal_test.xml'
            ), {}, 'init', False, 'test'
        )
        # self._load('account', 'test', 'account_minimal_test.xml')
        self.company = self.env.company
        self.company.loan_type = 'amount'
        self.company.loan_max = 5000
        self.company.loan_max_months = 6
        self.company.loan_contract_months = 24
        self.company.loan_allow_multiple = False
        self.company.loan_approve = False
        self.employee1 = self.env.ref('hr.employee_stw')
        self.employee2 = self.env.ref('hr.employee_mit')
        self.employee1.contract_id.state = 'draft'
        self.loan_account_id = self.env.ref('hr_loan.cas')
        self.payable_account_id = self.env.ref('hr_loan.a_pay')
        self.journal_id = self.env.ref('hr_loan.miscellaneous_journal')
        self.payment_journal_id = self.env.ref('hr_loan.cash_journal')
        self.env.ref('base.partner_admin').property_account_payable_id = \
            self.payable_account_id.id

    def test_loan(self):
        """ Test Scenario: test loan request workflow """
        # Create loan 1
        loan_1 = self.env['hr.loan'].create({
            'employee_id': self.employee1.id,
            'loan_amount': 8000,
            'installment': 8,
        })
        # submit loan request with employee with no running contract
        self.employee1.contract_id.state = 'draft'
        message = "You must have running contract"
        with self.assertRaisesRegex(UserError, message):
            loan_1.action_submit()
        self.employee1.contract_id.state = 'open'
        # submit loan request with amount more than loan_max config
        message = "Loan amount can't be greater than %d" % \
                  self.company.loan_max
        with self.assertRaisesRegex(UserError, message):
            loan_1.action_submit()
        loan_1.loan_amount = 5000
        # submit loan request with duration more than loan_max_months config
        message = "NO of installment can't be greater than %d" % \
                  self.company.loan_max_months
        with self.assertRaisesRegex(UserError, message):
            loan_1.action_submit()
        loan_1.installment = 5
        # submit loan request with contract duration
        # more than loan_contract_months config
        message = "%d Months should passed from the start of " \
                  "your contract to request a loan" % \
                  self.company.loan_contract_months
        with self.assertRaisesRegex(UserError, message):
            loan_1.action_submit()
        self.company.loan_contract_months = 0
        # submit loan request
        loan_1.action_submit()
        self.assertEqual(loan_1.state, 'waiting_approval_1')
        # approve loan request without installment
        message = "You must compute installment before Approved"
        with self.assertRaisesRegex(UserError, message):
            loan_1.action_approve()
        # Generate installment
        loan_1.generate_installment()
        self.assertTrue(loan_1.loan_line_ids)
        # approve loan request without Loan Account
        message = "You must enter Loan Account to approve."
        with self.assertRaisesRegex(UserError, message):
            loan_1.action_approve()
        loan_1.loan_account_id = self.loan_account_id.id
        # approve loan request without journal
        message = "You must enter journal to approve."
        with self.assertRaisesRegex(UserError, message):
            loan_1.action_approve()
        loan_1.journal_id = self.journal_id.id
        # approve loan request without Account Payable
        message = "You must enter address with Account " \
                  "Payable for employee to approve."
        with self.assertRaisesRegex(UserError, message):
            loan_1.action_approve()
        loan_1.account_payable_id = self.payable_account_id.id
        # approve loan request
        loan_1.action_approve()
        self.assertEqual(loan_1.state, 'approve')
        # register loan payment
        self.employee1.address_home_id = self.env.ref('base.partner_admin').id
        payment = self.env['hr.loan.register.payment.wizard'].with_context(
            active_ids=loan_1.id, default_amount=loan_1.total_amount)
        with Form(payment) as pay:
            pay.journal_id = self.payment_journal_id
            payment += pay.save()
        payment.loan_post_payment()
        self.assertEqual(loan_1.payments_paid, True)
        # Create payslip for employee to pay installments
        payslip = self.env['hr.payslip'].create({
            'name': 'Payslip of Richard',
            'employee_id': self.employee1.id,
        })
        payslip._onchange_employee()
        # payslip.struct_id.journal_id = self.journal_id.id
        self.assertTrue(payslip.compute_sheet())
        self.assertIn('Loan',
                      payslip.mapped('input_line_ids.input_type_id.name'))
        payslip.action_payslip_done()
        self.assertTrue(all(payslip.input_line_ids.mapped('loan_line_id.paid')))
        self.assertEqual(self.employee1.loan_count,
                         len(self.employee1.loan_ids))
        self.assertEqual(self.employee1.loan_amount,
                         sum(self.employee1.mapped('loan_ids.loan_amount')))
        loan_action = self.employee1.action_view_loans()
        self.assertEqual(loan_action['domain'],
                         [('id', 'in', self.employee1.loan_ids.ids)])

        # Create loan 2
        message = "The employee has already a pending installment"
        with self.assertRaisesRegex(UserError, message):
            self.env['hr.loan'].create({
                'employee_id': self.employee1.id,
                'loan_amount': 3000,
                'installment': 3,
            })
        # allow multiple config
        self.company.loan_allow_multiple = True
        loan_2 = self.env['hr.loan'].create({
            'employee_id': self.employee1.id,
            'loan_amount': 3000,
            'installment': 3,
        })
        unpaid_amount = sum(self.env['hr.loan.line'].sudo().search([
            ('employee_id', '=', loan_2.employee_id.id),
            ('paid', '=', False), ('loan_id.state', '=', 'approve'),
        ]).mapped('amount'))
        amount = self.company.loan_max - unpaid_amount
        # check multiple loans amount validation
        message = "Loan amount can't be greater than %d" % amount
        with self.assertRaisesRegex(UserError, message):
            loan_2.action_submit()
        # check multiple approve
        self.company.loan_allow_multiple = False
        self.company.loan_approve = True
        self.company.loan_type = 'percentage'
        self.company.loan_max = 50
        self.employee2.address_home_id = self.env.ref('base.partner_admin').id

        # Create loan 2
        loan_3 = self.env['hr.loan'].create({
            'employee_id': self.employee2.id,
            'loan_amount': 5000,
            'installment': 3,
            'loan_account_id': self.loan_account_id.id,
            'journal_id': self.journal_id.id,
        })
        max_amount = \
            self.employee2.contract_id.wage * (self.company.loan_max / 100)
        message = "Loan amount can't be greater than %d" % max_amount
        with self.assertRaisesRegex(UserError, message):
            loan_3.action_submit()
        loan_3.loan_amount = max_amount
        loan_3.action_submit()
        loan_3.generate_installment()
        loan_3.action_approve()
        self.assertEqual(loan_3.state, 'waiting_approval_2')
        loan_3.action_double_approve()
        self.assertEqual(loan_3.state, 'approve')
        message = 'You cannot delete a loan which is not ' \
                  'in draft or cancelled state'
        with self.assertRaisesRegex(UserError, message):
            loan_3.unlink()
        loan_3.action_refuse()
        self.assertEqual(loan_3.state, 'refuse')
        loan_3.action_cancel()
        self.assertEqual(loan_3.state, 'cancel')
        loan_3.unlink()
