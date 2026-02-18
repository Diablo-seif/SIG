""" HR Employee Documents Lines """

from odoo import api, fields, models


class HrEmployeeDocumentsLines(models.Model):
    """ HR Employee Documents Lines """
    _name = 'hr.employee.documents.lines'
    _description = 'Employee Documents Lines'

    employee_id = fields.Many2one(
        'hr.employee',
        ondelete='cascade'
    )
    document_id = fields.Many2one(
        'hr.employee.documents',
        required=True
    )
    has_expiration = fields.Boolean(
        related='document_id.has_expiration',
        store=True
    )
    require_original = fields.Boolean(
        related='document_id.require_original',
        store=True
    )
    is_original = fields.Boolean()
    attachment = fields.Binary()
    title = fields.Char()
    expiry_date = fields.Date()

    @api.onchange('document_id')
    def _onchange_employee_id(self):
        """
        Get domain to filter documents that selected in any line before
        :return: dictionary with domain for document_id field
        """
        doc = self.employee_id.mapped('document_line_ids.document_id')
        return {'domain': {
            'document_id': [('id', 'not in', doc.ids)]
        }}
