""" Update object hr.payslip.run """

import base64
from datetime import datetime
from io import BytesIO

import xlwt
from xlwt import Formula
from xlwt import Utils

from odoo import _, models
from odoo.exceptions import UserError


# pylint: disable=no-member
class HrPayslipRun(models.Model):
    """ Update object hr.payslip.run  """
    _inherit = 'hr.payslip.run'

    # pylint: disable=invalid-name, too-many-statements, too-many-branches
    # pylint: disable=too-many-locals, undefined-loop-variable
    def export_payslip_batche(self):
        """
        Function Print Payslip Batches Excel File
        :return: link to download excel file
        """
        self.ensure_one()
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet(_('Payslip Batches'))
        lang = self.env.user.lang
        if "ar" in lang:
            worksheet.cols_right_to_left = 1

        worksheet.col(0).width = 256 * 10
        worksheet.col(1).width = 256 * 50
        worksheet.col(2).width = 256 * 30
        table_header = xlwt.easyxf(
            'font: bold 1, name Tahoma, color-index black,height 160;'
            'align: vertical center, horizontal center, wrap off;'
            'borders: left thin, right thin, top thin, bottom thin;'
            'pattern: pattern solid, pattern_fore_colour tan,'
            'pattern_back_colour tan'
        )

        table_header_batch = xlwt.easyxf(
            'font: bold 1, name Tahoma, color-index black,height 160;'
            'align: vertical center, horizontal center, wrap off;'
            'borders: left thin, right thin, top thin, bottom thin;'
            'pattern: pattern solid, pattern_fore_colour light_green,'
            'pattern_back_colour light_green'
        )
        header_format = xlwt.easyxf(
            'font: bold 1, name Aharoni , color-index black,height 160;'
            'align: vertical center, horizontal center, wrap off;'
            'alignment: wrap 1;'
            'borders: left thin, right thin, top thin, bottom thin;'
            'pattern: pattern solid, pattern_fore_colour gray25, '
            'pattern_back_colour gray25'
        )

        table_header_Data = table_header
        table_header_Data.num_format_str = '#,##0.00_);(#,##0.00)'
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
        table_data_o = xlwt.easyxf(
            'font: bold 1, name Aharoni, color-index black,height 150;'
            'align: vertical center, horizontal center, wrap off;'
            'borders: left thin, right thin, top thin, bottom thin;'
            'pattern: pattern solid, pattern_fore_colour gray11, '
            'pattern_back_colour gray11'
        )
        style_line_data = style_line
        style_line_data.num_format_str = '#,##0.00_);(#,##0.00)'
        for one in self:
            if not one.slip_ids:
                raise UserError(_('No Payslips In This Batch.'))
        # map code, name and sequence
        salary_rules = one.slip_ids.mapped('line_ids').mapped(
            lambda rule: (rule.code, rule.name, rule.sequence))
        # map sort rules based on code then name
        sorted_rules = sorted(salary_rules,
                              key=lambda tup: (tup[2], tup[1]))
        # unique rules based on code and create list of names and codes
        seen = set()
        array_codes = []
        array_codes_name = []
        # pylint: disable=unused-variable
        for code, name, sequence in sorted_rules:
            if code not in seen:
                seen.add(code)
                array_codes.append(code)
                array_codes_name.append(name)

        worksheet.panes_frozen = True
        worksheet.set_horz_split_pos(3)
        worksheet.set_vert_split_pos(3)

        for one in self:
            now = datetime.now()
            date = now.strftime('%Y-%m-%d')
            xls_file_path = (_('Payslip_Batches_%s.xls')) % (date)

            output = BytesIO()

            row = 0
            worksheet.row(row).height = 256 * 5

            worksheet.write_merge(row, row, 0, 2, _('Payslip Batch'),
                                  table_header_batch)
            worksheet.write_merge(row, row, 3, 5, _('Payslip Batch Start Date'),
                                  table_header_batch)
            worksheet.write_merge(row, row, 6, 8, _('Payslip Batch End Date'),
                                  table_header_batch)

            row = 1
            date_format = style_line
            date_format.num_format_str = 'dd/mm/yyyy'
            worksheet.row(row).height = 256 * 3
            worksheet.write_merge(row, row, 0, 2, one.name, style_line)
            worksheet.write_merge(row, row, 3, 5, one.date_start, date_format)
            worksheet.write_merge(row, row, 6, 8, one.date_end, date_format)

            row = 2
            worksheet.row(row).height = 256 * 5
            worksheet.write(row, 0, _('Reference'), header_format)
            worksheet.write(row, 1, _('Payslip'), header_format)
            worksheet.write(row, 2, _('Employee'), header_format)

            i = 3
            for rule_name in array_codes_name:
                worksheet.write(row, i, rule_name, header_format)

                i += 1
            row += 1
            for slip_id in one.slip_ids:
                if row % 2:
                    style_line = table_data
                else:
                    style_line = table_data_o

                worksheet.row(row).height = 256 * 5
                worksheet.write(row, 0, slip_id.number, style_line)
                worksheet.write(row, 1, slip_id.name, style_line)
                worksheet.write(row, 2, slip_id.employee_id.name, style_line)
                i = 3
                for code in array_codes:
                    have = False
                    for line in slip_id.line_ids:
                        if line.code == code:
                            have = True
                            worksheet.write(row, i, line.total, style_line)
                    if not have:
                        worksheet.write(row, i, '', style_line)
                    i += 1
                row += 1
            worksheet.row(row).height = 256 * 4
            worksheet.write_merge(row, row, 0, 2, _('Total'),
                                  table_data_tolal_line)
            len_array = len(array_codes)
            h = 3
            for l in range(0, len_array):
                sum_cell = Utils.rowcol_to_cell(3, l + 3)
                to_sum_cell = Utils.rowcol_to_cell(row - 1, l + 3)
                worksheet.write(
                    row, h,
                    Formula("SUM(" + sum_cell + ":" + to_sum_cell + ")"),
                    table_data_tolal_line
                )
                h += 1
            h += 1
            workbook.save(output)
            attachment_model = self.env['ir.attachment']
            attachment_model.search([('res_model', '=', 'hr.payslip.run'),
                                     ('res_id', '=', self.id)]).unlink()
            attachment_obj = attachment_model.create({
                'name': xls_file_path,
                'res_model': 'hr.payslip.run',
                'res_id': self.id,
                'type': 'binary',
                'datas': base64.b64encode(output.getvalue()),
            })

            # Close the String Stream after saving it in the attachments
            output.close()
            url = '/web/content/%s/%s' % (attachment_obj.id, xls_file_path)
            return {'type': 'ir.actions.act_url', 'url': url, 'target': 'new'}
