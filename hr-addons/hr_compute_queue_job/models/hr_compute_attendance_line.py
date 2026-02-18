""" init object hr.compute.attendance.line """

from odoo import fields, models, api


# pylint: disable=no-member
class HrComputeAttendanceLine(models.Model):
    """ init object hr.compute.attendance.line """
    _inherit = 'hr.compute.attendance.line'

    def schedule_compute_line(self):
        """
        Action Schedule Compute Line.
        """
        self.compute_line()

    def re_progress(self):
        """
        Action re_progress.
        """
        self.ensure_one()
        if self.queue_job_id:
            self.queue_job_id.requeue()

    @api.depends('queue_uuid')
    def _compute_queue_job_id(self):
        """
        Compute queue_job_id.
        """
        for rec in self:
            q_job_id = self.env['queue.job'].search([
                ('model_name', '=', 'hr.compute.attendance.line'),
                ('method_name', '=', 'schedule_compute_line'),
                ('uuid', '=', rec.queue_uuid),
            ], limit=1)
            if q_job_id:
                rec.queue_job_id = q_job_id.id

    queue_uuid = fields.Char()
    queue_job_id = fields.Many2one(comodel_name="queue.job",
                                   compute=_compute_queue_job_id,
                                   compute_sudo=True, store=True, )
    state = fields.Selection(string="Status", related="queue_job_id.state",
                             store=True)
    exc_info = fields.Text(related="queue_job_id.exc_info")
