""" Integration Test HR Applicant """
from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestHrApplicant(TransactionCase):
    """ Unit Test for test_hr_applicant model """

    def test_action_job_offer_send(self):
        """ Test Scenario: test action_job_offer_send() """
        application = self.env.ref('hr_recruitment.hr_case_financejob1')

        # Test approve and sign application
        approver = self.env.ref('base.user_demo')
        with self.assertRaises(ValidationError):
            application.action_approve()

        application.with_user(approver.id).action_approve()
        self.assertEqual(
            application.sign_signature, approver.sign_signature)
        self.assertTrue(application.activity_ids)

        job_offer = self.env['hr.job.offer'].create({
            'applicant_id': application.id,
        })
        # Test that smart btn will list all created job offers
        action = application.action_view_job_offers()
        self.assertEqual(
            action['domain'], [('id', 'in', job_offer.ids)])

        template = self.env.ref('hr_job_offer.job_offer_mail_template_id')

        # Test that send job offer btn
        offer = job_offer.action_job_offer_send()
        self.assertEqual(
            offer['context']['default_template_id'], template.id)
        self.assertTrue(offer['context']['default_use_template'])
        self.assertEqual(job_offer.generate_date, fields.Datetime.now())

        # Test that print job offer btn
        job_offer.report_print()
        self.assertEqual(job_offer.generate_date, fields.Datetime.now())

        job_offer.action_approve()
        self.assertEqual(job_offer.state, 'approved')
        model = self.env.ref('hr_job_offer.model_hr_job_offer')
        reason = self.env['action.reason'].sudo().create({
            'name': 'Reason',
            'model_id': model.id,
        })
        job_offer_to_reject = self.env['hr.job.offer'].create({
            'applicant_id': application.id,
        })
        reject_reason_offer = self.env['job.offer.reject'].with_context(
            active_ids=job_offer_to_reject.ids).create({
                'action_reason_ids': [(4, reason.id)],
                'note': 'Reason note',
            })
        reject_reason_offer.action_reject()
        self.assertEqual(
            job_offer_to_reject.action_reason_ids, reason
        )
        self.assertEqual(
            job_offer_to_reject.note, reject_reason_offer.note
        )
        self.assertEqual(
            job_offer_to_reject.state, 'rejected'
        )
