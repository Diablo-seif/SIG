""" update object hr.payroll.structure to add effect rule"""

from odoo import models, api


class HrPayrollStructure(models.Model):
    """ update object hr.payroll.structure to add default effect rules"""
    _inherit = 'hr.payroll.structure'

    @api.model
    def default_get(self, fields_list):
        """
        add addition adn deduction rules when create new salary structure
        :param default_fields:
        :return:
        """
        res = super().default_get(fields_list)
        if res.get('rule_ids') and fields_list:
            default_rule_ids = res.get('rule_ids')
            new_rules = [
                (0, 0, {
                    'name': 'Addition',
                    'sequence': 50,
                    'code': 'ADD',
                    'category_id': self.env.ref('hr_payroll.ALW').id,
                    'condition_select': 'none',
                    'amount_select': 'code',
                    'amount_python_compute':
                        "result = employee.get_effects_payroll('additions',"
                        " payslip.date_from, payslip.date_to, code=False)",
                }),
                (0, 0, {
                    'name': 'Deduction',
                    'sequence': 150,
                    'code': 'DED',
                    'category_id': self.env.ref('hr_payroll.DED').id,
                    'condition_select': 'none',
                    'amount_select': 'code',
                    'amount_python_compute':
                        "result = employee.get_effects_payroll('deductions',"
                        " payslip.date_from, payslip.date_to, code=False)",
                }),
            ]
            res.update({"rule_ids": default_rule_ids + new_rules})
        return res
