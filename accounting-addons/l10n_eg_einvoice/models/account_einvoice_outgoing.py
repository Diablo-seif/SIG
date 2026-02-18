""" Initialize account.einvoice.outgoing """
import base64
import requests
import ssl
import urllib3
from ast import literal_eval
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

IDENTITY_SERVICE = {
    'testing': 'https://id.preprod.eta.gov.eg',
    'production': 'https://id.eta.gov.eg',
}


class CustomHttpAdapter(requests.adapters.HTTPAdapter):
    '''Transport adapter" that allows us to use custom ssl_context.'''

    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_context=self.ssl_context)


def get_session():
    session = requests.session()
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.options |= 0x4
    session.mount('https://', CustomHttpAdapter(ctx))
    return session


class AccountEInvoiceOutgoing(models.Model):
    """ outgoing tool to record any request sent to e-invoice """
    _name = 'account.einvoice.outgoing'
    _description = 'Egypt E-Invoice Outgoing'
    _order = 'id desc'
    _rec_name = 'action_type'

    action_type = fields.Selection(selection=[
        ('submit', 'Submit E-Invoice'),
        ('cancel', 'Cancel E-Invoice'),
        ('printout', 'Printout'),
        ('get_detail', 'Get Invoice Details'),
    ])
    last_date_sent = fields.Datetime(string='Last Sent Date', copy=False)
    move_ids = fields.Many2many(comodel_name='account.move',
                                string='Invoice / Credit')
    method = fields.Selection(
        selection=[('post', 'POST'), ('get', 'GET'), ('put', 'PUT'),
                   ('patch', 'PATCH'), ('delete', 'DELETE')], required=True)
    request_url = fields.Char(required=True)
    request_header = fields.Text(required=True, default='{}')
    request_data = fields.Text(required=True, default='{}')
    request_params = fields.Text(required=True, default='{}')
    result = fields.Text(copy=False)
    error = fields.Text(copy=False)
    state = fields.Selection(selection=[('new', 'New'), ('sent', 'Sent')],
                             default='new',
                             copy=False)

    @api.model
    def login_as_taxpayer_system(self, journal_id):
        """ get access token """
        url = IDENTITY_SERVICE[journal_id.einvoice_purpose]
        client_id = journal_id.client_id
        client_secret = journal_id.client_secret
        token = self.env['taxpayer.token'].search([
            ('expire_date', '>', fields.Datetime.now()),
            ('company_id', '=', journal_id.company_id.id),
            ('client_id', '=', client_id),
            ('client_secret', '=', client_secret),
            ('url', '=', url),
        ], limit=1)
        if token:
            return token.access_token
        payload = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'InvoicingAPI',
        }
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
        }
        respond = get_session().post(
            '%s/connect/token' % url,
            data=payload,
            headers=headers,
        ).json()
        error_msg = respond.get('error', False)
        if error_msg:
            raise ValidationError(error_msg)
        access_token = respond.get('access_token')
        expires_in = respond.get('expires_in')
        expire_date = fields.Datetime.now() + relativedelta(seconds=expires_in)
        self.env['taxpayer.token'].create({
            'access_token': access_token,
            'expire_date': expire_date,
            'company_id': journal_id.company_id.id,
            'client_id': journal_id.client_id,
            'client_secret': journal_id.client_secret,
            'url': url,
        })
        return access_token

    # pylint: disable=cell-var-from-loop,undefined-loop-variable
    def action_submit(self):
        """ submit documents to e-invoice"""
        self.write({'last_date_sent': fields.Datetime.now()})
        for record in self.filtered(
                lambda r: r.state != 'sent' and r.action_type == 'submit'):
            url = record.request_url
            method = record.method
            data = record.request_data
            headers = literal_eval(record.request_header)
            result = get_session().request(method, url,
                                           data=data.encode('utf-8'),
                                           headers=headers).json()
            record.result = result
            record.state = 'sent'
            if result:
                submission_id = result.get('submissionId')
                accepted_documents = result.get('acceptedDocuments', [])
                for document in accepted_documents:
                    # @formatter:off
                    record.move_ids.filtered(
                        lambda r: r.name == document.get('internalId')).write({
                        'einvoice_uuid': document.get('uuid'),
                        'einvoice_submit_uuid': submission_id,
                        'einvoice_state': 'submitted',
                    })
                    # @formatter:on
                rejected_documents = result.get('rejectedDocuments', [])
                for document in rejected_documents:
                    msg = '\n'.join([
                        f"{detail.get('code')}: {detail.get('message')}"
                        for detail in
                        document.get('error', {}).get('details', [])
                    ])
                    # @formatter:off
                    record.move_ids.filtered(
                        lambda r: r.name == document.get('internalId')).write({
                        'einvoice_message': msg,
                        'einvoice_state': 'submit_issue',
                    })
                    # @formatter:on
                try:
                    errors = result.get('error', {}).get('details', [])
                except AttributeError:
                    errors = result.get('error', {})

                if errors and isinstance(errors, str):
                    msg = errors
                else:
                    msg = '\n'.join([
                        f"{error.get('code')}: {error.get('message')}"
                        for error in errors])
                if msg:
                    record.move_ids.write({
                        'einvoice_message': msg,
                        'einvoice_state': 'submit_issue',
                    })
                    record.error = errors

    @api.model
    def _auto_submit(self):
        """ This method is called from a cron job.
        It is used to submit invoices.
        """
        records = self.search([('state', '=', 'new'),
                               ('action_type', '=', 'submit')])
        records.action_submit()

    def action_printout(self):
        """ get pdf from ETA """
        self.write({'last_date_sent': fields.Datetime.now()})
        for record in self.filtered(
                lambda r: r.state != 'sent' and r.action_type == 'printout'):
            url = record.request_url
            method = record.method
            data = record.request_data
            headers = literal_eval(record.request_header)
            result = get_session().request(method, url, data=data,
                                           headers=headers)
            record.result = result
            record.state = 'sent'
            if result.status_code == 200:
                for move in record.move_ids:
                    attachment = self.env['ir.attachment'].create({
                        'name': "E-Invoice %s - %s.pdf" % (move.name,
                                                           move.einvoice_state),
                        'datas': base64.b64encode(result.content),
                        'type': 'binary',
                        'res_model': 'account.move',
                        'res_id': move.id,
                    })
                    msg = (_("E-Invoice PDF"))

                    move.with_context(no_new_invoice=True).message_post(
                        body=msg, attachment_ids=[attachment.id])
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                    }
            else:
                raise ValidationError(
                    _("Please try get E-Invoice printout later!"))

    def action_cancel(self):
        """ send request to ETA to cancel invoice """
        self.write({'last_date_sent': fields.Datetime.now()})
        for record in self.filtered(
                lambda r: r.state != 'sent' and r.action_type == 'cancel'):
            url = record.request_url
            method = record.method
            request_data = record.request_data
            headers = literal_eval(record.request_header)
            result = get_session().request(method=method, url=url,
                                           data=request_data,
                                           headers=headers)
            response = result.json()
            record.result = response
            record.state = 'sent'
            if result.status_code == 200:
                record.move_ids.write({"einvoice_state": "waiting_cancel"})
                for move in record.move_ids:
                    move.message_post(
                        body=(_("E-Invoice is waiting cancelled")))
            else:
                error = response.get('error', {})
                error_code = error.get('code', 'Error')
                error_details = error.get('details')
                msg = error_code + '\n'
                msg += '\n'.join([
                    f"{error_detail.get('target')}: "
                    f"{error_detail.get('message')}"
                    for error_detail in error_details])
                raise ValidationError(_(msg))

    def action_get_details(self):
        """ get einvoice update from ETA """
        self.write({'last_date_sent': fields.Datetime.now()})
        for record in self.filtered(
                lambda r: r.state != 'sent' and r.action_type == 'get_detail'):
            url = record.request_url
            method = record.method
            headers = literal_eval(record.request_header)
            result = get_session().request(method=method, url=url,
                                           headers=headers)
            response = result.json()
            record.result = response
            record.state = 'sent'
            if result.status_code == 200:
                return response
            if result.status_code == 404:
                msg = _("You are not allowed to get E-Invoice information")
            else:
                msg = _("ETA can be reached right now, Please try again later")
            raise ValidationError(msg)
