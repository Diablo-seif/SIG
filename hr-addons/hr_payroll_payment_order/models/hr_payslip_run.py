""" Update object hr.payslip.run """
import base64
from datetime import datetime
from io import BytesIO

import xlwt

from odoo import _, fields, models


# pylint: disable=no-member,protected-access,cell-var-from-loop,too-many-locals
class HrPayslipRun(models.Model):
    """ Update object hr.payslip.run """
    _inherit = "hr.payslip.run"

    payment_order_line_ids = fields.One2many(
        comodel_name='hr.payslip.payment.order.line',
        inverse_name='payslip_run_id',
    )
    payment_count = fields.Integer(
        compute='_compute_payment_count',
        readonly=True,
    )
    last_payment_excel = fields.Binary(
        attachment=True,
        copy=False,
    )

    def _compute_payment_count(self):
        """
        count number of payment
        """
        for record in self:
            record.payment_count = \
                len(record.mapped('payment_order_line_ids.payment_id'))

    def action_open_payment(self):
        """
        open payment form or list related to payslip
        """
        payments = self.mapped('payment_order_line_ids.payment_id')
        action = self.env["ir.actions.actions"]._for_xml_id(
            "hr_payroll_payment_order.hr_payslip_payment_order_action")
        if len(payments) > 1:
            action['domain'] = [('id', 'in', payments.ids)]
        elif len(payments) == 1:
            form_view = [(self.env.ref(
                'hr_payroll_payment_order.hr_payslip_payment_order_form').id,
                          'form')]
            if 'views' in action:
                action['views'] = form_view + \
                                  [(state, view) for state, view in
                                   action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = payments.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'create': False,
        }
        action['context'] = context
        return action

    def action_export_payment_order(self):
        """
        extract excel for each payment order line related to batch
        """
        self.ensure_one()
        now = datetime.now()
        date = now.strftime('%Y-%m-%d')
        xls_file_path = (_('Payslip_Payment_%s.xls')) % date
        workbook = xlwt.Workbook()
        output = BytesIO()
        table_header = xlwt.easyxf(
            'font: bold 1, name Tahoma, color-index black,height 160;'
            'align: vertical center, horizontal center, wrap off;'
            'borders: left thin, right thin, top thin, bottom thin;'
            'pattern: pattern solid, pattern_fore_colour tan,'
            'pattern_back_colour tan'
        )

        header_format = xlwt.easyxf(
            'font: bold 1, name Aharoni , color-index black,height 160;'
            'align: vertical center, horizontal center, wrap off;'
            'alignment: wrap 1;'
            'borders: left thin, right thin, top thin, bottom thin;'
            'pattern: pattern solid, pattern_fore_colour gray25, '
            'pattern_back_colour gray25'
        )
        table_header_data = table_header
        table_header_data.num_format_str = '#,##0.00_);(#,##0.00)'
        style_line = xlwt.easyxf(
            'align: vertical center, horizontal center, wrap off;',
            'borders: left thin, right thin, top thin, bottom thin; '
            # 'num_format_str: General'
        )

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
        domain = [('payslip_run_id', '=', self.id),
                  ('payment_id.state', 'in', ['draft', 'validated'])]
        payments = self.env['hr.payslip.payment.order.line'].search(domain)
        payment_methods = payments.mapped('payment_method_id')

        for payment_method in payment_methods:
            worksheet = workbook.add_sheet(payment_method.name)
            lang = self.env.user.lang
            if "ar" in lang:
                worksheet.cols_right_to_left = 1
            row = 0
            worksheet.write(row, 0, _('Employee Name'), header_format)
            worksheet.write(row, 1, _('Bank'), header_format)
            worksheet.write(row, 2, _('Account Number'), header_format)
            worksheet.write(row, 3, _('Paid Amount'), header_format)
            row += 1
            # @formatter:off
            payments_related = payments.filtered(
                lambda payslip_line: payslip_line.payment_method_id ==
                payment_method)
            # @formatter:on
            total_paid = 0
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
            sum_cell = xlwt.Utils.rowcol_to_cell(1, 3)
            to_sum_cell = xlwt.Utils.rowcol_to_cell(row - 1, 3)
            worksheet.write(
                row, 3,
                xlwt.Formula("SUM(" + sum_cell + ":" + to_sum_cell + ")"),
                table_data_tolal_line)
        workbook.save(output)
        self.last_payment_excel = base64.b64encode(output.getvalue())
        output.close()
        url = '/web/content/hr.payslip.run/%s/last_payment_excel/%s' \
              % (self.id, xls_file_path)
        return {'type': 'ir.actions.act_url', 'url': url, 'target': 'new'}
