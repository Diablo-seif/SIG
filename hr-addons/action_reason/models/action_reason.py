""" Action Reason """
from odoo import api, fields, models, _


class ActionReason(models.Model):
    """ Action Reason """
    _name = 'action.reason'
    _description = 'Action Reason'
    _sql_constraints = [
        ('unique_name', 'UNIQUE(name,model_id)', _('Reason must be unique')),
    ]
    name = fields.Char(required=True, string='Reason')
    res_model = fields.Char()
    model_id = fields.Many2one(
        'ir.model', compute='_compute_model',
        inverse='_inverse_model', store=True
    )
    color = fields.Integer(default=1)

    @api.depends('res_model')
    def _compute_model(self):
        """ get model id from res model name value """
        for rec in self:
            rec.model_id = self.env['ir.model'].search(
                [('model', '=', rec.res_model)]
            ).id

    def _inverse_model(self):
        """ Inverse res model from model id """
        for rec in self:
            rec.res_model = rec.model_id.model or False
