""" Inherited res partner"""

from odoo import models, fields


class ResPartner(models.Model):
    """inherit res.partner to add tax details"""
    _inherit = 'res.partner'

    legal_entity_type_id = fields.Many2one(
        'legal.entity.type',
    )
    tax_card_number = fields.Char()
    tax_file_number = fields.Char()
    vat_department_id = fields.Many2one(
        'vat.department',
        "VAT Department",
    )
    vat = fields.Char(
        string='Tax Registration Number',
    )
    national_id = fields.Char(
        string="National ID",
    )
