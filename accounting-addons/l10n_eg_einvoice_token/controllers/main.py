""" implement token api """
import json
import ast
import threading

from odoo import http, SUPERUSER_ID
from odoo.exceptions import AccessError
from odoo.http import request


# pylint: disable=no-member, unused-argument, no-self-use
class AccountEInvoice(http.Controller):
    """ implement token api """

    @http.route(['/api/einvoices'], type="http", auth="api_key", csrf=False,
                methods=['GET'])
    def get_invoice_waiting_sign(self, **kw):
        """ retrieve invoices waiting sign """
        request_incoming = request.env["account.einvoice.token.log"]
        print(request.httprequest.data)
        jsondata = request.httprequest.data
        if jsondata:
            jsondata = ast.literal_eval(
                request.httprequest.data.decode('utf-8'))
        request_incoming = request_incoming.with_user(SUPERUSER_ID).create({
            "request_url": request.httprequest.base_url,
            "request_header": request.httprequest.headers,
            "request_data": jsondata,
            "request_params": request.httprequest.query_string,
            "request_method": request.httprequest.method,
        })
        if not not getattr(threading.currentThread(), 'testing', False):
            request.env.cr.commit()
        values = {}
        try:
            invoices = request.env['account.move'].search(
                [('move_type', 'in', ['out_invoice', 'out_refund']),
                 ('state', '=', 'posted'),
                 ('einvoice_state', '=', 'waiting_sign'),
                 ('journal_id.submit_einvoice', '=', True),
                 ])
            if invoices:
                invoices_data = \
                    invoices.prepare_invoice_json(signed=False,
                                                  documents_object=False)
                values['success'] = True
                values['invoices'] = json.loads(invoices_data)

                values['count'] = len(invoices)
            else:
                values['success'] = False
                values['error_code'] = 1
                values['error_message'] = 'No invoices need signature!'

        except AccessError:
            values = {'success': False,
                      'error_message': 'You are not allowed access invoice'}
        request_incoming.write({
            'result': values
        })
        return json.dumps(values)

    @http.route(['/api/einvoice'], type="http", auth="api_key",
                csrf=False, methods=['POST'])
    def update_invoice_signature(self, **kw):
        """ add signature in invoice """
        jsondata = ast.literal_eval(request.httprequest.data.decode('utf-8'))
        request_incoming = request.env["account.einvoice.token.log"]
        request_incoming = request_incoming.with_user(SUPERUSER_ID).create({
            "request_url": request.httprequest.base_url,
            "request_header": request.httprequest.headers,
            "request_data": jsondata,
            "request_params": request.httprequest.query_string,
            "request_method": request.httprequest.method,
        })
        if not not getattr(threading.currentThread(), 'testing', False):
            request.env.cr.commit()
        signature = jsondata.get('signature')
        invoice_id = False
        if 'invoice_id' in request.params:
            invoice_id = request.params['invoice_id']
        if invoice_id and isinstance(invoice_id, str) and signature:
            try:
                invoice = request.env['account.move'].search(
                    [('move_type', 'in', ['out_invoice', 'out_refund']),
                     ('state', '=', 'posted'),
                     ('name', '=', invoice_id),
                     ('journal_id.submit_einvoice', '=', True),
                     ], limit=1)
                if invoice:
                    if invoice.einvoice_state == 'waiting_sign':
                        invoice.write({
                            'einvoice_signature': signature,
                            'einvoice_state': 'waiting_submit'
                        })
                        values = {'success': True,
                                  'success_message':
                                      'Invoice %s is signed successfully'
                                      % invoice.name}
                    else:
                        values = {'success': False,
                                  'error_message': 'Invoice %s is signed '
                                                   'before!' % invoice.name}
                else:
                    values = {'success': False,
                              'error_message': 'Invoice %s is '
                                               'not found!' % invoice_id}
            except AccessError:
                values = {'success': False,
                          'error_message': 'You are not allowed access invoice'}

        else:
            values = {'success': False,
                      'error_message': 'Invoice is not found or '
                                       'no signature received!'}
        request_incoming.write({
            'result': values
        })
        return json.dumps(values)
