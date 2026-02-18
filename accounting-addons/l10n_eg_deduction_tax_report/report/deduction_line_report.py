"""init model """

from odoo import tools
from odoo import models, fields, api


class DeductionLineReport(models.Model):
    """
    deduction Tax report using sql view
    to generate all data needed to this report
    """
    _name = "deduction.line.report"
    _description = "Deduction Tax Report"
    _auto = False
    _rec_name = 'payment_id'

    payment_id = fields.Many2one('account.payment', readonly=True)
    deduction_tax_id = fields.Many2one('account.tax', readonly=True)
    transaction_base_amount = fields.Monetary(readonly=True)
    tax_amount = fields.Monetary(readonly=True)
    transaction_total_amount = fields.Monetary(readonly=True)
    tax_percentage = fields.Integer(readonly=True, group_operator=None)
    currency_id = fields.Many2one('res.currency', readonly=True)
    vat_department = fields.Char(
        readonly=True,
        string="Related Department Code"
    )
    tax_type = fields.Selection([
        ('deduction', 'Deduction'),
        ('withholding', 'Withholding'),
    ], readonly=True)
    payment_date = fields.Date(readonly=True)
    transaction_date = fields.Char(readonly=True)
    transaction_type = fields.Char(readonly=True)
    duration = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
    ], readonly=True)
    year = fields.Integer(readonly=True, group_operator=None)
    month = fields.Integer(readonly=True)
    deduction_type = fields.Selection([
        ('unspecified', '1'),
        ('returns', '2'),
        ('com_return', '3'),
        ('discount', '4'),
    ], readonly=True)
    vendor_name = fields.Char(readonly=True)
    vendor_address = fields.Char(readonly=True)
    file_number = fields.Char(readonly=True)
    national_id = fields.Char(string="National ID", readonly=True)
    registration_number = fields.Char(readonly=True)
    currency_label = fields.Char(related='currency_id.currency_unit_label')
    currency_code = fields.Integer(string="Currency",
                                   compute='_compute_currency_code')

    # pylint: disable=no-self-use
    @api.model
    def _select(self):
        return """
            SELECT
                row_number() OVER () AS id,
                tax.deduction_code as transaction_type,
                line.payment_id,
                line.deduction_tax_id,
                line.base_amount as transaction_base_amount,
                ABS(line.tax_amount) as tax_amount,
                line.total_amount as transaction_total_amount,
                ABS(line.tax_percentage) as tax_percentage,
                line.tax_type,
                line.currency_id,
                move.date as payment_date,
                TO_CHAR(move.date  :: DATE, 'DD-MM-YYYY')
                as transaction_date,
                payment.deduction_type,
                partner.name as vendor_name,
                REPLACE(REPLACE(REPLACE(REPLACE(
                partner.vat,
                '-', ''), ',', ''), '/', ''), '.', '')
                as registration_number,
                REPLACE(REPLACE(REPLACE(REPLACE(
                partner.tax_file_number,
                '-', ''), ',', ''), '/', ''), '.', '')
                as file_number,
                partner.national_id,
                vat_dep.code as vat_department,
                REPLACE(REPLACE(REPLACE(REPLACE(
                concat_ws(' ', partner.street,
                partner.street2,partner.city,
                state.name),
                '-', ''), ',', ''), '/', ''), '.', '')
                as vendor_address,
                extract(year from move.date) as year,
                extract(month from move.date) as month,
                (CASE
                 WHEN extract(month from move.date) IN (1,2,3)
                 then '1'
                 WHEN extract(month from move.date) IN (4,5,6)
                 then '2'
                 WHEN extract(month from move.date) IN (7,8,9)
                 then '3'
                 ELSE '4'
                 END) duration
        """

    # pylint: disable=no-self-use
    @api.model
    def _from(self):
        return '''
            FROM account_payment_deduction_line line
            LEFT JOIN account_payment payment ON payment.id = line.payment_id
            LEFT JOIN account_move move ON move.id = payment.move_id
            LEFT JOIN account_tax tax ON tax.id = line.deduction_tax_id
            LEFT JOIN res_partner partner ON partner.id = payment.partner_id
            LEFT JOIN vat_department vat_dep
            ON vat_dep.id = partner.vat_department_id
            LEFT JOIN res_country_state state ON
            state.id = partner.state_id
        '''

    # pylint: disable=no-self-use
    @api.model
    def _where(self):
        return '''
        where line.payment_id IS NOT NULL and
        line.tax_type = 'deduction' and
        move.state = 'posted'
        '''

    # pylint: disable=no-self-use
    @api.model
    def _group_by(self):
        return '''
            GROUP BY
                line.payment_id,
                line.deduction_tax_id,
                line.base_amount,
                line.tax_amount,
                line.total_amount,
                line.tax_percentage,
                line.currency_id,
                line.tax_type,
                move.date,
                payment.deduction_type,
                partner.name,
                partner.vat,
                partner.tax_file_number,
                partner.national_id,
                line.deduction_tax_id,
                partner.street,
                partner.street2,
                partner.city,
                vat_dep.code,
                state.name,
                tax.deduction_code
        '''

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        # pylint: disable=sql-injection
        self.env.cr.execute('''
            CREATE OR REPLACE VIEW %s AS (
                %s %s %s %s
            )
        ''' % (
            self._table, self._select(), self._from(), self._where(),
            self._group_by()
        ))

    @api.depends('currency_id')
    def _compute_currency_code(self):
        """
        compute currency_code from currency
        this codes as in income tax website
        """
        currency_codes = {
            self.env.ref('base.EGP'): 1,
            self.env.ref('base.USD'): 2,
            self.env.ref('base.GBP'): 3,
            self.env.ref('base.EUR'): 4,
            self.env.ref('base.SAR'): 5,
            self.env.ref('base.AED'): 6,
        }
        for line in self:
            line.currency_code = currency_codes.get(line.currency_id, 0)
