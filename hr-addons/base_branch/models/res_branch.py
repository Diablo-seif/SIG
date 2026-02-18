""" Initialize Res Branch """

from odoo import api, fields, models


class ResBranch(models.Model):
    """ Res Branches Model """
    _name = 'res.branch'
    _description = 'Branches'
    _inherit = "mail.thread"
    _check_company_auto = True
    _order = 'active desc, name'
    _sql_constraints = [
        (
            "code_company_uniq",
            "unique (code,company_id)",
            "The code of the Branch must be unique per company!",
        ),
        (
            "name_company_uniq",
            "unique (name,company_id)",
            "The name of the Branch must be unique per company!",
        ),
    ]

    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company
    )
    partner_id = fields.Many2one(
        'res.partner', delegate=True, required=True,
        ondelete='cascade'
    )
    manager_id = fields.Many2one('res.users')
    name = fields.Char(
        required=True,
        related='parent_id.name',
        inherited=True,
        store=True,
        readonly=False
    )
    code = fields.Char(required=True)
    users_ids = fields.One2many(
        'res.users',
        'branch_id'
    )
    latitude = fields.Float(
        string='Geo Latitude',
        digits=(16, 5)
    )
    longitude = fields.Float(
        string='Geo Longitude',
        digits=(16, 5)
    )
    allowed_dimension = fields.Char()
    parent_id = fields.Many2one(
        'res.branch'
    )
    child_ids = fields.One2many(
        'res.branch',
        'parent_id'
    )
    tag_ids = fields.Many2many(
        'res.branch.tag',
        string='Tags'
    )

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

    def name_get(self):
        """
            Override name_get:
             - change display_name to be code - name
        """
        return self.mapped(lambda r: (r.id, f'{r.code} - {r.name}'))
