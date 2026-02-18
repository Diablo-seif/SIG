""" Update object hr.payslip.run """
from odoo import api, fields, models


# pylint: disable=no-member
class HrPayslipRun(models.Model):
    """ Update object hr.payslip.run  """
    _inherit = 'hr.payslip.run'

    def schedule_compute_batch(self):
        """
        Schedule compute payslips batch.
        """
        for record in self:
            for payslip in record.slip_ids:
                if payslip.compute_job_id:
                    payslip.compute_job_id.requeue()
                else:
                    env_job = payslip.with_delay(
                        priority=1).schedule_compute_sheet()
                    if env_job and env_job.uuid:
                        payslip.uuid_compute_job = env_job.uuid

    def re_schedule_all_compute_batch(self):
        """
        Re-Schedule Failed Compute payslips batch.
        """
        for record in self:
            for payslip in record.slip_ids:
                if payslip.compute_job_id:
                    payslip.compute_job_id.requeue()

    def re_schedule_failed_compute_batch(self):
        """
        Re-Schedule Failed Compute payslips batch.
        """
        for record in self:
            if record.slip_ids:
                for payslip in record.slip_ids:
                    if payslip.compute_status in ['failed']:
                        payslip.compute_job_id.requeue()

    def schedule_batch_done(self):
        """
        Schedule compute batch Done.
        """
        for record in self:
            for payslip in record.slip_ids:
                env_job = payslip.with_delay(
                    priority=1).schedule_payslip_done()
                if env_job and env_job.uuid:
                    payslip.uuid_confirm_job = env_job.uuid

    def re_schedule_failed_batch_done(self):
        """
        Re-Schedule Failed confirm payslips batch.
        """
        for record in self:
            if record.slip_ids:
                for payslip in record.slip_ids:
                    if payslip.confirm_status in ['failed']:
                        payslip.confirm_job_id.requeue()

    def schedule_send_batch(self):
        """
        Schedule send batch.
        """
        for record in self:
            for payslip in record.slip_ids:
                payslip.with_delay(priority=1).schedule_send_payslip()
            record.mark_as_send = True

    def compute_payslips(self):
        """
        Function to Re-compute Payslips
        """
        for record in self:
            for payslip in record.slip_ids:
                payslip.compute_sheet()

    def action_confirm(self):
        """
        Fucntion to confirm batches
        :return:
        """
        for record in self:
            for payslip in record.slip_ids:
                payslip.action_payslip_done()
            record.confirm_manual = True

    def action_send(self):
        """
        Function send payslips by email
        :return:
        """
        for record in self:
            for payslip in record.slip_ids:
                payslip.action_payslip_send_only()
            record.mark_as_send = True

    @api.depends('slip_ids')
    def _compute_payslip_count(self):
        """
        function compute count payslips
        """
        for rec in self:
            rec.payslip_count = len(rec.slip_ids)

    @api.depends('payslip_count', 'slip_ids', 'slip_ids.compute_status',
                 'slip_ids.compute_job_id')
    def _compute_compute_progress(self):
        """
        function compute_progress.
        """
        for rec in self:
            compute_progress = -1
            if rec.slip_ids and rec.slip_ids[0].compute_job_id:
                c_count_done = len(rec.slip_ids.filtered(
                    lambda slip: slip.compute_status == 'done'))
                compute_progress = (c_count_done / rec.payslip_count) * 100
            rec.compute_progress = compute_progress

    @api.depends('payslip_count', 'slip_ids', 'slip_ids.confirm_status',
                 'slip_ids.confirm_job_id')
    def _compute_confirm_progress(self):
        """
        function confirm_progress.
        """
        for rec in self:
            confirm_progress = -1
            if rec.slip_ids and rec.slip_ids[0].confirm_job_id:
                c_count_done = len(rec.slip_ids.filtered(
                    lambda slip: slip.confirm_status == 'done'))
                confirm_progress = (c_count_done / rec.payslip_count) * 100
            rec.confirm_progress = confirm_progress

    @api.depends('compute_progress', 'confirm_progress', 'confirm_manual')
    def _compute_state(self):
        """
        Compute State.
        """
        for rec in self:
            if rec.confirm_manual:
                rec.state = "confirmed"
            elif rec.compute_progress == -1 and rec.confirm_progress == -1:
                rec.state = 'draft'
            else:
                if rec.confirm_progress == 100:
                    rec.state = "confirmed"
                elif rec.confirm_progress > 0:
                    rec.state = "confirm_progress"
                else:
                    if rec.compute_progress == 100:
                        rec.state = "computed"
                    elif rec.compute_progress >= 0:
                        rec.state = "compute_progress"

    mark_as_send = fields.Boolean(string="Email has been sent")
    payslip_count = fields.Integer(compute='_compute_payslip_count', store=True)
    state = fields.Selection(string='Status',
                             selection_add=[
                                 ('compute_progress', 'In Compute Progress'),
                                 ('computed', 'Computed'),
                                 ('confirm_progress', 'In Confirm Progress'),
                                 ('confirmed', 'Confirmed')],
                             compute='_compute_state', store=True)
    compute_progress = fields.Float(compute='_compute_compute_progress',
                                    store=True)
    confirm_progress = fields.Float(compute='_compute_confirm_progress',
                                    store=True)
    confirm_manual = fields.Boolean()
