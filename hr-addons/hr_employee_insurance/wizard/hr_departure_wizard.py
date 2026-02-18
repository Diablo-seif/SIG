""" Initialize Hr Departure Wizard """

from odoo import fields, models


# pylint: disable=no-member
class HrDepartureWizard(models.TransientModel):
    """
        Inherit Hr Departure Wizard:
    """
    _inherit = 'hr.departure.wizard'

    resignation_received_date = fields.Date(
        string='Received Date (6)'
    )
    resignation_received_number = fields.Char(
        string='Received Number (6)'
    )

    def action_register_departure(self):
        """ Override action_register_departure """
        employee = self.employee_id
        employee.resignation_received_date = self.resignation_received_date
        employee.resignation_received_number = self.resignation_received_number
        history = employee.insurance_history_ids.filtered(
            lambda r: not r.date_to)
        if history:
            history.date_to = self.resignation_received_date
        return super().action_register_departure()
