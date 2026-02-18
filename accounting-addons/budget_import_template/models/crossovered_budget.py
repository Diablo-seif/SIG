""" Initialize Crossovered Budget """

from odoo import _, api, models


class CrossoveredBudget(models.Model):
    """
        Inherit Crossovered Budget:
         - Add import template.
    """
    _inherit = 'crossovered.budget'

    # pylint: disable=no-self-use
    @api.model
    def get_import_templates(self):
        """ :return default import template """
        return [{
            'label': _('Import template for budgets'),
            'template':
                '/budget_import_template/static/xlsx/crossovered.budget.xlsx'
        }]
