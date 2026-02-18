""" Inherit HR Applicant to add  job offer"""
from odoo import models


class HrApplicant(models.Model):
    """ inherit HR Applicant to add more needed fields """
    _inherit = 'hr.applicant'

    # pylint: disable=no-member
    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        res = super().create_employee_from_applicant()
        res['context'].update({
            'default_contract_type_id': self.job_id.contract_type_id.id,
            'default_country_id': self.country_id.id,
        })
        return res
