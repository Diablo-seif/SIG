""" implement token api """
import json
import ast
import re

from odoo import http, SUPERUSER_ID

from odoo.http import request, Response, JsonRequest
from odoo.tools import date_utils


def _json_response(self, result=None, error=None):
    einvoice = False
    if hasattr(self.endpoint, 'routing'):
        einvoice = self.endpoint.routing.get('einvoice')
    if einvoice:
        response = {}
        if error is not None:
            response['error'] = error
        if result is not None:
            response['result'] = result
        if isinstance(result, str) and not error:
            response = json.loads(result)

        mime = 'application/json'
        body = json.dumps(response, default=date_utils.json_default)

        return Response(
            body, status=error and error.pop('http_status', 200) or 200,
            headers=[('Content-Type', mime), ('Content-Length', len(body))]
        )

    response = {
        'jsonrpc': '2.0',
        'id': self.jsonrequest.get('id')
    }
    if error is not None:
        response['error'] = error
    if result is not None:
        response['result'] = result

    mime = 'application/json'
    body = json.dumps(response, default=date_utils.json_default)

    return Response(
        body, status=error and error.pop('http_status', 200) or 200,
        headers=[('Content-Type', mime), ('Content-Length', len(body))]
    )


setattr(JsonRequest, '_json_response', _json_response)


# pylint: disable=no-member, unused-argument, no-self-use
class AccountEInvoice(http.Controller):
    """ implement token api """

    @http.route(['/api/einvoice/external/Ping'], type="json", auth="public",
                csrf=False, einvoice=True)
    def einvoice_ping(self, **kw):
        """ verify einvoice ETA website ownership via company VAT number """
        # make sure that ETA send data
        authorization = request.httprequest.headers.get('Authorization')
        request_incoming = request.env["account.einvoice.incoming"]
        status_code = "401 Unauthorized"
        if request_incoming.einvoice_auth_validation(authorization):
            jsondata = ast.literal_eval(
                request.httprequest.data.decode('utf-8'))
            request_incoming = \
                request_incoming.with_user(SUPERUSER_ID).create({
                    "request_url": request.httprequest.base_url,
                    "request_header": request.httprequest.headers,
                    "request_data": jsondata,
                    "request_params": request.httprequest.query_string,
                    "request_method": request.httprequest.method,
                })
            received_vat = jsondata.get('Rin')
            vat = request.env.company.vat
            vat_formatted = ''.join(re.findall('[0-9]+', vat))
            if vat_formatted == received_vat:
                values = {'Rin': vat_formatted}
                status_code = "200"
            else:
                values = {"error": "VAT not matched"}
                status_code = "403"
        else:
            values = {"error": "Authorization not matched"}
        if request_incoming:
            request_incoming.write({"result": values})
        Response.status = status_code
        return json.dumps(values)

    # pylint: disable=too-many-locals
    @http.route(['/api/einvoice/external/notifications/documents'],
                type="json", auth="public", csrf=False, einvoice=True)
    def einvoice_receive_notification(self, **kw):
        """ receive einvoice ETA website notifications """
        authorization = request.httprequest.headers.get('Authorization')
        request_incoming = request.env["account.einvoice.incoming"]
        status_code = "401"
        values = {"error": "Authorization not matched"}
        # make sure that ETA send data
        if request_incoming.einvoice_auth_validation(authorization):
            jsondata = \
                ast.literal_eval(request.httprequest.data.decode('utf-8'))
            request_id = jsondata.get('DeliveryId')
            if request_id:
                # make sure request does not received before
                old_request_id = \
                    request_incoming.with_user(SUPERUSER_ID).search(
                        [("request_id", "=", request_id)])
                status_code = "200"
                if not old_request_id:
                    request_type = jsondata.get('Type') or ""
                    request_message = jsondata.get('Message') or ""
                    request_incoming = \
                        request_incoming.with_user(SUPERUSER_ID).create({
                            "request_id": request_id,
                            "request_type": request_type,
                            "request_message": request_message,
                            "request_url": request.httprequest.base_url,
                            "request_header": request.httprequest.headers,
                            "request_data": jsondata,
                            "request_params": request.httprequest.query_string,
                            "request_method": request.httprequest.method,
                        })
                    for message in request_message:
                        invoice_uuid = message.get("UUId")
                        invoice_submit_uuid = message.get("SubmissionUUId")
                        invoice_number = message.get("InternalId")
                        invoice_status = message.get("Status")
                        invoice_type = message.get("Type")
                        if invoice_type == "Received":
                            request_incoming.create_incoming_document(
                                invoice_uuid, invoice_submit_uuid,
                                invoice_number)
                        else:
                            request_incoming.update_invoice_status(
                                invoice_uuid, invoice_number, invoice_status)
                    values = {"message": "200 OK"}
                else:
                    values = {"message": "Duplicate notification"}
            else:
                status_code = "406"
                values = {"message": "No message id received"}
        if request_incoming:
            request_incoming.write({"result": values})
        Response.status = status_code
        return json.dumps(values)
