""" Initialize Res Company """

from odoo import api, fields, models


class ResCompany(models.Model):
    """
        Inherit Res Company:
         -
    """
    _inherit = 'res.company'

    proposal_sequence_id = fields.Many2one(
        'ir.sequence'
    )

    def _create_proposal_sequence(self):
        """  Create Sequence """
        for rec in self:
            if not rec.proposal_sequence_id:
                rec.proposal_sequence_id = self.env['ir.sequence'].sudo().create({
                    'name': f"{rec.name} proposal",
                    'code': rec.name,
                    'prefix': 'PROP/',
                    'padding': 4,
                    'number_next': 1,
                    'number_increment': 1,
                    'company_id': rec.id,
                })

    @api.model
    def create(self, vals_list):
        """
            Override create method
             - sequence name
        """
        res = super().create(vals_list)
        res._create_proposal_sequence()
        return res
