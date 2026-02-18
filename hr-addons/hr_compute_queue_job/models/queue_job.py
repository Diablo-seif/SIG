""" init object queue.job"""

from odoo import models, api


class QueueJob(models.Model):
    """ init object  queue.job"""
    _inherit = 'queue.job'

    # pylint: disable=no-self-use
    @api.model
    def create(self, vals_list):
        """
        Override create to add sequence.
        :param vals:
        """
        if 'name' not in vals_list or not vals_list.get('name', False):
            vals_list['name'] = self.env['ir.sequence'].next_by_code(
                'queue.job') or ' '
        return super(QueueJob, self).create(vals_list)

    def _message_post_on_failure(self):
        """
        Override to stop send on failure
        """
        return
