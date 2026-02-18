""" init model symbiotic contribution Calculation """

from odoo import models, fields


class SymbioticContributionComputation(models.TransientModel):
    """
    symbiotic contribution Calculation wizard
    """
    _name = "symbiotic.contribution.computation"
    _description = "Symbiotic Contribution Calculation Wizard"

    year = fields.Integer()

    def action_compute(self):
        """  call action_compute_symbiotic_contribution """
        return self.env['symbiotic.contribution'].\
            action_compute_symbiotic_contribution(self.year)
