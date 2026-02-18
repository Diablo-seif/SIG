"""init model """

from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class VatSalesReport(models.Model):
    """
    VAT Tax report using sql view
    to generate all data needed to this report
    """
    _name = "vat.sales.report"
    _description = "VAT Tax Report"
    _auto = False
    _order = "invoice_type desc, invoice_tax_adjustment desc, invoice_date," \
             "invoice_no"

    id = fields.Integer(readonly=True)
    move_id = fields.Many2one('account.move', readonly=True)
    line_id = fields.Many2one('account.move.line', readonly=True)
    product_id = fields.Many2one('product.product', readonly=True)

    document_type = fields.Char(readonly=True)
    tax_type = fields.Char(readonly=True)
    table_product_type = fields.Char(readonly=True)
    invoice_no = fields.Char(readonly=True)
    partner_name = fields.Char(readonly=True)
    registration_number = fields.Char(readonly=True)
    file_number = fields.Char(readonly=True)
    partner_address = fields.Char(readonly=True)
    national_no = fields.Char(readonly=True)
    partner_mobile = fields.Char(readonly=True)
    invoice_date = fields.Char(readonly=True)
    product_name = fields.Char(readonly=True)
    product_code = fields.Char(readonly=True)
    product_type = fields.Selection([('local', '1'),
                                     ('consu', '3'),
                                     ('service', '4'),
                                     ('adjustment', '5')],
                                    readonly=True)
    product_type_name = fields.Selection([('consu', 'Stock'),
                                          ('local', 'Local'),
                                          ('service', 'Service'),
                                          ('adjustment', 'Adjustment')],
                                         readonly=True)
    product_kind = fields.Char(readonly=True)
    product_uom = fields.Char(readonly=True)
    price_unit = fields.Float(readonly=True, group_operator=None)
    tax_percentage = fields.Float(readonly=True, group_operator=None)
    quantity = fields.Float(readonly=True, group_operator=None)
    price_subtotal = fields.Monetary(readonly=True, group_operator=None)
    tax_amount = fields.Monetary(readonly=True)
    price_total = fields.Monetary(string='Total', readonly=True)
    total_tax_with_sign = fields.Monetary(readonly=True)
    currency_id = fields.Many2one('res.currency', readonly=True)
    year = fields.Integer(readonly=True)
    month = fields.Integer(readonly=True)
    year_month = fields.Integer(readonly=True, string="Year Month 'YYYYMM'")
    tax_adjustment_year_month = \
        fields.Integer(readonly=True, string="Adjustment Year Month 'YYYYMM'")
    invoice_type = fields.Selection(selection=[
        ('entry', 'Journal Entry'),
        ('out_invoice', 'Customer Invoice'),
        ('out_refund', 'Customer Credit Note'),
        ('in_invoice', 'Vendor Bill'),
        ('in_refund', 'Vendor Credit Note'),
        ('out_receipt', 'Sales Receipt'),
        ('in_receipt', 'Purchase Receipt')], string='Type', readonly=True)
    invoice_tax_adjustment = fields.Boolean(readonly=True)
    invoice_tax_adjustment_name = fields.Selection(readonly=True, selection=[
        ('invoice', 'Invoice'), ('bill', 'Bill'), ('adjustment', 'Adjustment')])
    invoice_tax_reported = fields.Boolean(readonly=True)

    # pylint: disable=no-self-use
    # pylint: disable=anomalous-backslash-in-string
    @api.model
    def _select(self):
        return """
            SELECT
                row_number() OVER () AS id,
                line.id as line_id,
                line.currency_id as currency_id,
                invoice.id as move_id,
                product.id as product_id,
                (CASE
                 WHEN invoice.move_type in ('out_invoice', 'in_invoice')
                 then '1'
                 WHEN invoice.move_type in ('out_refund', 'in_refund')
                 then '3'
                 ELSE '1'
                 END) document_type,
                (CASE
                 WHEN account_tax_group.tax_group_type ='vat'
                 then '1'
                 ELSE '2'
                 END) tax_type,
                (CASE
                 WHEN account_tax_group.tax_group_type ='vat'
                 then '0'
                 WHEN account_tax_group.table_tax_type ='table1'
                 then '1'
                 ELSE '2'
                 END) table_product_type,
                (CASE
                 WHEN invoice.move_type in ('in_invoice', 'in_refund')
                 and invoice.supplier_invoice_number != 0
                 then CAST(invoice.supplier_invoice_number as VARCHAR)
                 ELSE NULLIF(regexp_replace(invoice.name, '\\D','','g'), '')
                 END) as invoice_no,
                partner.name as partner_name,
                partner.vat as registration_number,
                (CASE
                 WHEN partner.parent_id > 0
                 then (SELECT tax_file_number FROM res_partner
                 where id = partner.parent_id)
                 ELSE partner.tax_file_number
                 END) as file_number,
                concat_ws(' ', partner.street,
                partner.street2,partner.city, state.name) AS partner_address,
                (CASE
                 WHEN partner.parent_id > 0
                 then (SELECT national_id FROM res_partner
                 where id = partner.parent_id)
                 ELSE partner.national_id
                 END) as national_no,
                partner.mobile as partner_mobile,
                TO_CHAR(invoice.invoice_date, 'DD/MM/YYYY') as invoice_date,
                product_template.name as product_name,
                regexp_replace(product.default_code, '[^\\w]+|_','')
                 as product_code,
                (CASE
                 WHEN invoice.tax_adjustment
                 then 'adjustment'
                 WHEN invoice.move_type in ('in_refund', 'out_refund')
                 then 'adjustment'
                 WHEN invoice.move_type in ('in_invoice')
                 then 'local'
                 ELSE product_template.type
                 END) as product_type,
                (CASE
                 WHEN invoice.tax_adjustment
                 then 'adjustment'
                 WHEN invoice.move_type in ('in_refund', 'out_refund')
                 then 'adjustment'
                 WHEN invoice.move_type in ('in_invoice')
                 then 'local'
                 ELSE product_template.type
                 END) as product_type_name,
                 (CASE
                 WHEN line_tax.vat_product_kind > 0
                 then CAST(line_tax.vat_product_kind AS varchar)
                 ELSE '0'
                 END) as product_kind,
                '1' as product_uom,
                line.price_unit as price_unit,
                account_tax.amount as tax_percentage,
                line.quantity as quantity,
                line.price_subtotal as price_subtotal,
                (CASE
                 WHEN invoice.move_type in ('out_invoice', 'in_refund')
                 then (line_tax.tax_amount * -1)
                 WHEN invoice.move_type in ('in_invoice', 'out_refund')
                 then line_tax.tax_amount
                 ELSE line_tax.tax_amount
                 END) as total_tax_with_sign,
                (CASE
                 WHEN line_tax.line_tax_one
                 then line.price_subtotal + line_tax.tax_amount
                 ELSE line_tax.tax_amount
                 END) as price_total,
                extract(year from invoice.invoice_date) as year,
                extract(month from invoice.invoice_date) as month,
                cast(to_char(invoice_date,'YYYYMM') as integer) as year_month,
                (CASE
                WHEN invoice.move_type = 'in_refund'
                then 'in_invoice'
                WHEN invoice.move_type = 'out_refund'
                then 'out_invoice'
                ELSE invoice.move_type
                END)as invoice_type,
                invoice.tax_adjustment as invoice_tax_adjustment,
                invoice.tax_adjustment_year_month
                 as tax_adjustment_year_month,
                (CASE
                 WHEN invoice.move_type ='out_invoice' and
                 invoice.tax_adjustment = False
                 then 'invoice'
                 WHEN invoice.move_type ='in_invoice' and
                 invoice.tax_adjustment = False
                 then 'bill'
                 WHEN  invoice.tax_adjustment = True
                 then 'adjustment'
                 WHEN invoice.move_type in ('in_refund', 'out_refund')
                 then 'adjustment'
                 ELSE 'invoice'
                 END) as invoice_tax_adjustment_name,
                invoice.tax_reported as invoice_tax_reported,
                (CASE
                 WHEN line_tax.tax_amount > 0
                 then line_tax.tax_amount
                 ELSE (line.price_total - line.price_subtotal)
                 END) as tax_amount
        """

    # pylint: disable=no-self-use
    @api.model
    def _from(self):
        return '''
            FROM account_move_line_account_tax_rel taxes
            LEFT JOIN account_move_line_tax line_tax
            ON line_tax.line_id = taxes.account_move_line_id and
            line_tax.tax_id = taxes.account_tax_id
            LEFT JOIN account_tax account_tax
            ON account_tax.id = taxes.account_tax_id
            LEFT JOIN account_tax_group account_tax_group ON
            account_tax_group.id = account_tax.tax_group_id
            INNER JOIN account_move_line line
            ON line.id = taxes.account_move_line_id
            LEFT JOIN product_product product ON product.id = line.product_id
            LEFT JOIN product_template product_template
            ON product_template.id = product.product_tmpl_id
            LEFT JOIN account_move invoice ON invoice.id = line.move_id
            LEFT JOIN res_partner partner ON partner.id = invoice.partner_id
            LEFT JOIN res_country_state state ON
            state.id = partner.state_id
        '''

    # pylint: disable=no-self-use
    @api.model
    def _where(self):
        return '''
        where line.move_id IS NOT NULL
        and line.exclude_from_invoice_tab = False
        and line_tax.move_id IS NOT NULL
        and invoice.state = 'posted'
        '''

    # pylint: disable=no-self-use
    @api.model
    def _order_by(self):
        return '''
        ORDER BY invoice_type
        '''

    # pylint: disable=sql-injection
    def init(self):
        """ prepare the report data """
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
            CREATE OR REPLACE VIEW %s AS (
                %s %s %s %s
            )
        ''' % (
            self._table, self._select(), self._from(), self._where(),
            self._order_by()
        ))

    def action_close_report(self):
        """  call close report wizard """
        active_ids = self.env.context.get('active_ids')
        ctx = dict(self.env.context)
        ctx.update({'report_model': 'vat.sales.report'})
        if not active_ids:
            raise UserError(_("There are no active invoice"))
        return {'name': _('Close report for month'),
                'res_model': 'vat.close.report',
                'view_mode': 'form',
                'view_id': self.env.ref('l10n_eg_vat.'
                                        'vat_close_report_view_form').id,
                'context': ctx,
                'target': 'new',
                'type': 'ir.actions.act_window'}

    # pylint: disable=too-many-arguments,redefined-outer-name
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        """ override to reverse the order of invoice type while group by """
        if 'invoice_type' in groupby:
            orderby = 'invoice_type DESC' + (orderby and (',' + orderby) or '')
        if 'invoice_tax_adjustment_name' in groupby:
            orderby = 'invoice_tax_adjustment_name DESC' + (
                orderby and (',' + orderby) or '')

        return super(VatSalesReport, self).read_group(
            domain, fields, groupby, offset=0, limit=limit,
            orderby=orderby, lazy=lazy
        )
