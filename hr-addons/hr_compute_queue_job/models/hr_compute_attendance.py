""" init object compute attendance"""

from odoo import fields, models, api


# pylint: disable=no-member
class HrComputeAttendance(models.Model):
    """ init object  hr.compute.attendance"""
    _inherit = 'hr.compute.attendance'

    def action_progress(self):
        """
        Action Progress.
        """
        self.action_compute(compute_direct=False)
        for compute_line in self.compute_ids:
            env_job = compute_line.with_delay(
                priority=1).schedule_compute_line()
            if env_job and env_job.uuid:
                compute_line.queue_uuid = env_job.uuid

    def action_re_progress(self):
        """
        Action Re progress.
        """
        for rec in self:
            for line in rec.compute_ids:
                if line.queue_job_id:
                    line.queue_job_id.requeue()

    def action_failed_progress(self):
        """
        Action Re progress for failed.
        """
        for rec in self:
            for line in rec.compute_ids:
                if line.queue_job_id and line.queue_job_id.state in ['failed']:
                    line.queue_job_id.requeue()

    @api.depends('progress')
    def _compute_state(self):
        """
        Compute State.
        """
        for rec in self:
            if rec.progress == -1:
                rec.state = 'draft'
            elif rec.progress == 100:
                rec.state = "done"
            else:
                rec.state = "in_progress"

    @api.depends('compute_ids', 'compute_ids.state')
    def _compute_progress(self):
        """
        Compute progress
        """
        for rec in self:
            progress = 0
            if rec.compute_ids:
                total_count = len(rec.compute_ids)
                done_count = len(rec.compute_ids.filtered(
                    lambda line: line.state == 'done'))
                progress = (done_count / total_count) * 100
            else:
                progress = -1
            rec.progress = progress

    @api.depends('compute_ids', 'compute_ids.state', 'count_lines')
    def _compute_done_count(self):
        """
        Compute Done Count.
        """
        for rec in self:
            done_count = 0
            if rec.compute_ids and rec.count_lines:
                done_count = (len(rec.compute_ids.filtered(
                    lambda line: line.state == 'done')) * 100 / rec.count_lines)
            rec.done_count = int(round(done_count))

    @api.depends('compute_ids', 'compute_ids.state', 'count_lines')
    def _compute_failed_count(self):
        """
        Compute Failed Count.
        """
        for rec in self:
            failed_count = 0
            if rec.compute_ids and rec.count_lines:
                failed_lines = rec.compute_ids.filtered(
                    lambda line: line.state == 'failed')
                failed_count = (len(failed_lines) * 100 / rec.count_lines)
            rec.failed_count = int(round(failed_count))

    @api.depends('compute_ids', 'compute_ids.state', 'count_lines')
    def _compute_progress_count(self):
        """
        Compute progress Count not done and failed.
        """
        for rec in self:
            progress_count = 0
            if rec.compute_ids and rec.count_lines:
                progress_count = (len(rec.compute_ids.filtered(
                    lambda line: line.state in ['pending', 'enqueued',
                                                'started'])) * 100 /
                                  rec.count_lines)
            rec.progress_count = int(round(progress_count))

    state = fields.Selection(string="Status",
                             selection=[('draft', 'Draft'),
                                        ('in_progress',
                                         'In Progress'),
                                        ('done', 'Done')],
                             compute=_compute_state, store=True, )
    progress = fields.Float(compute=_compute_progress, store=True)

    done_count = fields.Float(compute=_compute_done_count,
                              store=True)
    failed_count = fields.Float(compute=_compute_failed_count,
                                store=True)
    progress_count = fields.Float(compute=_compute_progress_count,
                                  store=True)
