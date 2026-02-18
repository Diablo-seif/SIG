""" Insurance Job """

from odoo import _, api, fields, models


class InsuranceJob(models.Model):
    """ Insurance Job  """
    _name = "insurance.job"
    _description = 'Insurance Job'
    _sql_constraints = [
        ('unique_name', 'UNIQUE(name,code)', 'Name must be unique')
    ]

    name = fields.Char(
        required=True,
        translate=True
    )
    code = fields.Char(
        required=True
    )

    def name_get(self):
        """ Override name_get to change displayed name """
        return [(rec.id, _("[%(code)s] %(name)s")
                 % {"code": rec.code, "name": rec.name}) for rec in self]

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """ Override name_search to change search with name or code """
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', operator, name), ('name', operator, name)]
        records = self.search(domain + args, limit=limit)
        return records.name_get()
