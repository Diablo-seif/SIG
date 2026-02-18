""" Inherit HR Job to add contract type and level """

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrJob(models.Model):
    """ inherit HR Job """
    _inherit = 'hr.job'

    salary_type = fields.Selection(
        [('fixed', 'Fixed'), ('range', 'Range')], default='fixed'
    )
    salary = fields.Monetary()
    min_salary = fields.Monetary()
    max_salary = fields.Monetary()
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id.id
    )
    manpower_line_ids = fields.One2many('hr.manpower.plan.line', 'job_id')

    @api.constrains('salary_type', 'min_salary', 'max_salary')
    def _check_salary(self):
        """ Validate that min """
        for rec in self:
            if rec.salary_type == 'range' and rec.min_salary > rec.max_salary:
                raise ValidationError(
                    _("Min salary can't be more than the max salary")
                )

    def name_get(self):
        """
        Override name_get to change displayed name with contract type job name
        """
        if self.env.context.get('job_with_contract_type'):
            return [(
                rec.id,
                _('%(level_name)s %(name)s %(contract_type_name)s') % {
                    "level_name": rec.sudo().job_level_id.name or '',
                    "name": rec.name or '',
                    "contract_type_name":
                        rec.sudo().contract_type_id and
                        '[%s]' % rec.contract_type_id.name or ''
                }
            ) for rec in self]
        return super(HrJob, self).name_get()
