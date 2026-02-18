
from odoo import models, fields


class JobGrade(models.Model):
    _name = 'sig.job.grade'

    name = fields.Char(required=True)
