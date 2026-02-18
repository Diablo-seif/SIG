""" Inherit HR employee to add documents field """

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID


class HrEmployee(models.Model):
    """ add employee required documents """
    _inherit = 'hr.employee'

    @api.model
    def _default_document_line_ids(self):
        """ get default employee required documents """
        default_docs = self.env['hr.employee.documents'].search(
            [('default_document', '=', True)])
        return [
            (0, 0, {
                'document_id': doc.id,
                'has_expiration': doc.has_expiration,
                'require_original': doc.require_original,
            }) for doc in default_docs
        ]

    document_line_ids = fields.One2many(
        'hr.employee.documents.lines', 'employee_id',
        default=_default_document_line_ids)

    # pylint: disable=protected-access
    @api.model
    def activity_expiry(self):
        """ Create Activity for expired documents """
        expiry = fields.date.today() + relativedelta(
            days=self.env.company.employee_document_expiry or 30)
        expired_docs = self.env['hr.employee.documents.lines'].search([
            ('expiry_date', '=', expiry),
            ('has_expiration', '=', True),
        ])
        for doc in expired_docs:
            user_id = doc.employee_id.hr_user_id.id or SUPERUSER_ID
            doc.employee_id._activity_schedule_with_view(
                'mail.mail_activity_data_todo',
                views_or_xmlid='hr.view_employee_tree',
                user_id=user_id,
                summary='%s will be expired by %s' % (
                    doc.document_id.name, doc.expiry_date
                )
            )
