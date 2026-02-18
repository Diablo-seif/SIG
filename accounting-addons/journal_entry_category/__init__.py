""" initialize whole module python packages """
from odoo import api, SUPERUSER_ID

from . import models


# pylint: disable=unused-argument,invalid-name
def uninstall_hook(cr, registry):
    """
    reset journal entry action to original context
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    action = env.ref('account.action_move_journal_line')
    context = "'default_move_type': 'entry', 'search_default_misc_filter':1, " \
              "'view_no_maturity': True}"
    action.write({'context': context})
