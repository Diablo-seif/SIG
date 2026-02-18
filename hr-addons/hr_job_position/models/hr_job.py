""" Inherit HR Job to add contract type and level """

from odoo import _, fields, models


class HrJob(models.Model):
    """ inherit HR Job """
    _inherit = 'hr.job'
    _sql_constraints = [
        ('name_company_uniq',
         'unique(name, company_id, department_id,'
         'contract_type_id, job_level_id)',
         _('The name of the job position must be'
           ' unique per department in company!')),
    ]
    contract_type_id = fields.Many2one(
        'hr.contract.type'
    )
    job_level_id = fields.Many2one(
        'hr.job.level'
    )

    # pylint: disable=no-member
    def name_get(self):
        """
        Override name_get to change displayed name with job title job name
        """
        return [(
            rec.id,
            _('%(level_name)s %(job_name)s') % {
                "level_name": rec.sudo().job_level_id.name or '',
                "job_name": rec.name or ''
            }
        ) for rec in self]
