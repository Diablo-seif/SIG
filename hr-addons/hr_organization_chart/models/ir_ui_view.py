""" Inherit view and action to add new view type """

from odoo import fields, models


class IrUiView(models.Model):
    """ inherit Ir Ui View to add new view type """
    _inherit = 'ir.ui.view'

    type = fields.Selection(
        selection_add=[('org_chart', 'Organization Chart')]
    )


class IrActionsActWindowView(models.Model):
    """ inherit Ir Actions Act Window View to add new view type """
    _inherit = 'ir.actions.act_window.view'

    view_mode = fields.Selection(
        selection_add=[('org_chart', 'Organization Chart')],
        ondelete={'org_chart': 'cascade'}
    )
