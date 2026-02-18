"""
    extend BaseModel to add x_approval_category_id field
    for all models in the registry
"""

from odoo import fields, models


class Base(models.AbstractModel):
    """
        Inherit Base:
         - 
    """
    _inherit = 'base'

    x_approval_category_id = fields.Many2one(
        'approval.category', string='Approval Category'
    )
