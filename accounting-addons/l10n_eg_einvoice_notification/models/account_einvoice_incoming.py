""" Initialize account.einvoice.outgoing """

from odoo import _, fields, models, api, SUPERUSER_ID


class AccounteInvoiceIncoming(models.Model):
    """ incoming tool to record any request received from ETA e-invoice """
    _name = 'account.einvoice.incoming'
    _description = 'Egypt E-Invoice Incoming'
    _order = 'id desc'
    _rec_name = 'request_url'

    request_url = fields.Char(required=True)
    request_method = fields.Char(required=True)
    request_header = fields.Text(required=True, default='{}')
    request_data = fields.Text(required=True, default='{}')
    request_params = fields.Text(required=True, default='{}')
    result = fields.Text(copy=False)

    request_id = fields.Char(string="Request ID")
    request_type = fields.Char()
    request_message = fields.Text()

    @api.model
    def einvoice_auth_validation(self, authorization):
        """ auth requests received from ETA """
        dbuuid = \
            self.env['ir.config_parameter'].sudo().get_param('database.uuid')
        if authorization.replace("ApiKey ", "") == dbuuid:
            return True
        return False

    @api.model
    def update_invoice_status(self, invoice_uuid, invoice_number,
                              invoice_status):
        """ find invoice and update status based on ETA """
        invoice = self.env["account.move"].with_user(SUPERUSER_ID).search(
            [("einvoice_uuid", "=", invoice_uuid),
             ("name", "=", invoice_number)], limit=1)
        if invoice:
            invoice.with_user(SUPERUSER_ID).write({
                "einvoice_state": invoice_status.lower()
            })
            if invoice_status in ["Cancelled", "Rejected", "Invalid"]:
                user = invoice.posted_by or invoice.write_uid
                # @formatter:off
                msg = \
                    _('Invoice has been %s, Please review!') % invoice_status
                todo_activity = \
                    self.env.ref('mail.mail_activity_data_todo', False)
                if todo_activity:
                    invoice.with_user(SUPERUSER_ID).with_context(
                        lang=user.lang).activity_schedule(
                            activity_type_id=todo_activity.id,
                            summary=msg,
                            user_id=user.id)
            invoice.with_user(SUPERUSER_ID).message_post(
                body=(_("Invoice is %s from ETA") % invoice_status))

    @api.model
    def create_incoming_document(self, invoice_uuid, invoice_submit_uuid,
                                 invoice_number):
        """ create record for received documents
        used to allow user to get vendor bill / refund """
        document_receive_obj = self.env["account.document.receive"]
        if invoice_uuid:
            document_receive_obj.with_user(SUPERUSER_ID).create({
                "invoice_uuid": invoice_uuid,
                "invoice_number": invoice_number,
                "invoice_submit_uuid": invoice_submit_uuid
            })
