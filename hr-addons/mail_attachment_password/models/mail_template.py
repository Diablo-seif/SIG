""" Init object mail.template """

import base64

import PyPDF2

from odoo import fields, models


class MailTemplate(models.Model):
    """ Init object mail.template """
    _inherit = 'mail.template'

    is_report_protected = fields.Boolean(string="Is Password on Report?",
                                         default=False)
    report_password = fields.Char(help="Set Password on pdf document.")

    # pylint: disable=unused-argument,no-member,redefined-outer-name
    # pylint: disable=too-many-locals
    def generate_email(self, res_ids, fields=None):
        """
        Overrider Generate Email.
        :param res_ids:
        :param fields:
        :return: res
        """
        res = super().generate_email(res_ids, fields=fields)
        if self.is_report_protected and self.report_password:
            for key, value in list(res[res_ids[0]].items()):
                if key == 'attachments':
                    password = str(self.report_password)
                    name = value[0][0]
                    bin_data = value[0][1]
                    new_pdf = base64.b64decode(bin_data)
                    open('/tmp/out.pdf', 'wb').write(new_pdf)
                    pdf_file = open('/tmp/out.pdf', 'rb')
                    pdf_reader = PyPDF2.PdfFileReader(pdf_file)
                    pdf_writer = PyPDF2.PdfFileWriter()
                    for page_num in range(pdf_reader.numPages):
                        pdf_writer.addPage(pdf_reader.getPage(page_num))
                    pdf_writer.encrypt(password)
                    result_pdf = open('/tmp/' + str(name), 'wb')
                    pdf_writer.write(result_pdf)
                    result_pdf.close()
                    with open('/tmp/' + str(name), "rb") as pdf_file:
                        encoded_string = base64.b64encode(pdf_file.read())
                    res[res_ids[0]]['attachments'] = [(name, encoded_string)]
        return res
