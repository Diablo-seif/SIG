""" init hr.payslip.payment.order """
import base64
from datetime import datetime
from io import BytesIO

import xlwt

from odoo import _, api, fields, models
from odoo.exceptions import UserError


# pylint: disable=no-member,protected-access,too-many-locals,cell-var-from-loop
class HrPayslipPaymentOrder(models.Model):
    """
    init hr.payslip.payment.order
    """
    _name = 'hr.payslip.payment.order'
    _description = 'Payment Order'
    _check_company_auto = True
    _order = 'name desc, id desc'
    _inherit = ['mail.thread']

    name = fields.Char(
        string='Number',
        required=True,
        default='/',
        copy=False,
    )
    payment_method_id = fields.Many2one(
        comodel_name='hr.payslip.payment.method',
        required=True,
        tracking=True,
        check_company=True,
        ondelete='restrict',
    )
    payment_date = fields.Date(
        required=True,
        default=fields.Date.today(),
        tracking=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.company,
        required=True,
        tracking=True,
        ondelete='restrict',
    )
    state = fields.Selection(
        string='Status',
        selection=[
            ('draft', 'Draft'),
            ('validated', 'Validated'),
            ('cancel', 'Cancel'),
        ],
        required=True,
        default='draft',
        copy=False,
        tracking=True,
    )
    line_ids = fields.One2many(
        comodel_name='hr.payslip.payment.order.line',
        inverse_name='payment_id',
        string='Payslips',
        copy=True,
    )
    paid_amount = fields.Float(
        compute='_compute_paid_amount',
        store=True,
        tracking=True,
    )
    last_payment_excel = fields.Binary(
        attachment=True,
        copy=False,
    )

    @api.depends('line_ids', 'line_ids.paid_amount')
    def _compute_paid_amount(self):
        """
        sum payslip amount paid
        """
        for record in self:
            record.paid_amount = sum(record.line_ids.mapped('paid_amount'))

    @api.model_create_multi
    def create(self, vals_list):
        """
        add sequence
        """
        for vals in vals_list:
            payment_date = None
            if 'payment_date' in vals:
                payment_date = vals.get('payment_date')
            if 'name' not in vals or vals['name'] == '/':
                vals['name'] = \
                    self.env['ir.sequence'].with_company(
                        vals.get('company_id')
                    ).with_context(
                        sequence_date=payment_date
                    ).next_by_code('hr.payslip.payment.order') or '/'
        return super(HrPayslipPaymentOrder, self).create(vals_list)

    def action_validate(self):
        """
        update status to be validate
        """
        if any(line.paid_amount <= 0 for line in self.mapped('line_ids')):
            raise UserError(_('You can not validate with zero paid lines'))
        self.write({
            'state': 'validated',
        })

    def action_cancel(self):
        """
        update status to be cancel
        """
        self.write({
            'state': 'cancel',
        })

    def action_draft(self):
        """
        update status to be draft
        """
        self.write({
            'state': 'draft',
        })

    def action_export_payment_order(self):
        """
        extract excel for each payment order line related to batch
        """
        now = datetime.now()
        date = now.strftime('%Y-%m-%d')
        xls_file_path = (_('Payslip_Payment_%s.xls')) % date
        workbook = xlwt.Workbook()
        output = BytesIO()
        header_format = xlwt.easyxf(
            'font: bold 1, name Aharoni , color-index black,height 160;'
            'align: vertical center, horizontal center, wrap off;'
            'alignment: wrap 1;'
            'borders: left thin, right thin, top thin, bottom thin;'
            'pattern: pattern solid, pattern_fore_colour gray25, '
            'pattern_back_colour gray25'
        )
        table_header = xlwt.easyxf(
            'font: bold 1, name Tahoma, color-index black,height 160;'
            'align: vertical center, horizontal center, wrap off;'
            'borders: left thin, right thin, top thin, bottom thin;'
            'pattern: pattern solid, pattern_fore_colour tan,'
            'pattern_back_colour tan'
        )
        style_line = xlwt.easyxf(
            'align: vertical center, horizontal center, wrap off;',
            'borders: left thin, right thin, top thin, bottom thin; '
        )
        table_header_data = table_header
        table_header_data.num_format_str = '#,##0.00_);(#,##0.00)'
        table_data = xlwt.easyxf(
            'font: bold 1, name Aharoni, color-index black,height 150;'
            'align: vertical center, horizontal center, wrap off;'
            'borders: left thin, right thin, top thin, bottom thin;'
            'pattern: pattern solid, pattern_fore_colour white, '
            'pattern_back_colour white'
        )
        table_data.num_format_str = '#,##0.00'
        xlwt.add_palette_colour("gray11", 0x11)
        workbook.set_colour_RGB(0x11, 222, 222, 222)
        table_data_tolal_line = xlwt.easyxf(
            'font: bold 1, name Aharoni, color-index white,height 200;'
            'align: vertical center, horizontal center, wrap off;'
            'borders: left thin, right thin, top thin, bottom thin;'
            'pattern: pattern solid, pattern_fore_colour blue_gray, '
            'pattern_back_colour blue_gray'
        )

        table_data_tolal_line.num_format_str = '#,##0.00'
        style_line_data = style_line
        style_line_data.num_format_str = '#,##0.00_);(#,##0.00)'
        payments = self
        payment_methods = payments.mapped('payment_method_id')

        for payment_method in payment_methods:
            row = 0
            worksheet = workbook.add_sheet(payment_method.name)
            lang = self.env.user.lang
            if "ar" in lang:
                worksheet.cols_right_to_left = 1

            worksheet.write(row, 0, _('Employee Name'), header_format)
            worksheet.write(row, 1, _('Bank'), header_format)
            worksheet.write(row, 2, _('Account Number'), header_format)
            worksheet.write(row, 3, _('Paid Amount'), header_format)
            row += 1
            total_paid = 0
            payments_related = payments.filtered(
                lambda line: payment_method == line.payment_method_id).line_ids
            for payment_line in payments_related:
                worksheet.write(
                    row, 0,
                    payment_line.payslip_id.employee_id.display_name,
                    style_line)
                worksheet.write(
                    row, 1,
                    payment_line.payslip_id.bank_id.display_name or '',
                    style_line)
                worksheet.write(
                    row, 2,
                    payment_line.payslip_id.bank_account_id.acc_number or '',
                    style_line)
                worksheet.write(row, 3, payment_line.paid_amount, style_line)
                row += 1
                total_paid += payment_line.paid_amount
            to_sum_cell = xlwt.Utils.rowcol_to_cell(row - 1, 3)
            sum_cell = xlwt.Utils.rowcol_to_cell(1, 3)
            worksheet.write(
                row, 3,
                xlwt.Formula("SUM(" + sum_cell + ":" + to_sum_cell + ")"),
                table_data_tolal_line)
        workbook.save(output)
        self.last_payment_excel = base64.b64encode(output.getvalue())
        output.close()
        url = '/web/content/hr.payslip.payment.order/%s/last_payment_excel/%s' \
              % (self.id, xls_file_path)
        return {'type': 'ir.actions.act_url', 'url': url, 'target': 'new'}

    def unlink(self):
        if any(record.state not in ('draft', 'cancel') for record in self):
            raise UserError(_('You cannot delete a payment '
                              'which is not draft or cancelled!'))
        return super(HrPayslipPaymentOrder, self).unlink()

    def name_get(self):
        """
        Override Name Get.
        """
        res = []
        for rec in self:
            dis_name = "%s - %s - %s - %s" \
                       "" % (rec.name, rec.payment_method_id.name,
                             rec.payment_date, rec.paid_amount)
            res.append((rec.id, dis_name))
        return res
