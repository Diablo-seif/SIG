""" Initialize Invoice Activity Type """

from odoo import api, fields, models


class InvoiceActivityType(models.Model):
    """
        Initialize Invoice Activity Type:
    """
    _name = 'invoice.activity.type'
    _description = 'Invoice Activity Type'

    code = fields.Char(required=True)
    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)

    def name_get(self):
        """
            Override name_get:
             - change display_name to be code - name
        """
        return [
            (rec.id, '%s%s%s' %
             (rec.code or '', rec.code and ' - ' or '', rec.name))
            for rec in self
        ]

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """
            Override name_search:
             - search with name and code
        """
        args = list(args or [])
        if name:
            args.extend(['|', ('code', operator, name),
                         ('name', operator, name)])
        records = self.search(args, limit=limit)
        return records.name_get()
