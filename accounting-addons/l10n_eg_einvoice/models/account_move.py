""" Initialize Account Move """

import json
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

SYSTEM_API = {
    'testing': 'https://api.preprod.invoicing.eta.gov.eg',
    'production': 'https://api.invoicing.eta.gov.eg',
}
DOCUMENT_TYPE = {
    'out_invoice': 'I',
    'out_refund': 'C',
    'debit_note': 'D',
}


class AccountMove(models.Model):
    """
        Inherit Account Move:
    """
    _inherit = 'account.move'

    einvoice_uuid = fields.Char(string='E-Invoice UUID', readonly=True,
                                copy=False)
    einvoice_submit_uuid = fields.Char(string='E-Invoice Submit UUID',
                                       readonly=True, copy=False)
    einvoice_message = fields.Text(string='Message', readonly=True, copy=False)
    einvoice_signature = fields.Text(string='E-Invoice Signature', copy=False)
    einvoice_state = fields.Selection(
        [('waiting_post', 'Draft'), ('waiting_sign', 'Waiting Sign'),
         ('waiting_submit', 'Waiting Submit'), ('in_queue', 'In Queue'),
         ('submitted', 'Submitted'), ('valid', 'Validated'),
         ('submit_issue', 'Submit Issue'), ('rejected', 'Rejected'),
         ('invalid', 'Validation Issue'),
         ('waiting_cancel', 'Waiting Cancellation'),
         ('cancelled', 'Cancelled')], copy=False, string='E-Invoice Status',
        default='waiting_post', tracking=True,
        readonly=True)
    posted_by = fields.Many2one('res.users', readonly=True, copy=False)
    use_eg_invoice = fields.Boolean(related='journal_id.submit_einvoice')

    # pylint: disable=no-member,protected-access,too-many-branches
    def _validate_partner_data(self, record, record_type='customer'):
        """
        validate partner and company information
        """
        self.ensure_one()

        if not record.country_id.code:
            raise ValidationError(_('Missing %s country code') % record_type)
        if not record.state_id.name:
            raise ValidationError(_('Missing %s state') % record_type)
        if not record.city:
            raise ValidationError(_('Missing %s city') % record_type)
        if not record.street and not record.street2:
            raise ValidationError(_('Missing %s street') % record_type)
        if not record.building_number:
            raise ValidationError(_('Missing %s building number') % record_type)
        if record_type == 'company':
            if not record.invoice_activity_type_id:
                raise ValidationError(_('Missing company activity type'))
            activity_code = record.invoice_activity_type_id.code
            if not activity_code:
                raise ValidationError(_('Missing company activity type code'))
        min_vat_amount = self.journal_id.min_individual_vat_amount
        check_vat = True
        if record_type == 'customer':
            if not record.receiver_type:
                raise ValidationError(_('Missing receiver type'))
            is_person = bool(record.receiver_type == 'P')
            if is_person and self.amount_total_signed < min_vat_amount:
                check_vat = False
        if not record.get_einvoice_vat() and check_vat:
            raise ValidationError(_('Missing %s vat / ID') % record_type)
        if not record.name:
            raise ValidationError(_('Missing %s name') % record_type)

    # pylint: disable=no-member,protected-access
    def _einvoice_validate_data(self):
        """
        validate data required to send einvoice
        """
        for record in self:
            record._validate_partner_data(record.commercial_partner_id,
                                          record_type='customer')
            record._validate_partner_data(record.company_id,
                                          record_type='company')
            record.mapped("invoice_line_ids")._einvoice_validate_data()

    # pylint: disable=no-member
    def _post(self, soft=True):
        """
        Override action_post to add posted by to get notify about any issue
        """
        res = super(AccountMove, self)._post(soft)
        invoices = self.filtered(lambda inv: inv.journal_id.submit_einvoice)
        invoices._einvoice_validate_data()
        invoice_waiting_sign = invoices.filtered(
            lambda inv: inv.journal_id.einvoice_version == '1.0')
        invoice_waiting_submit = invoices.filtered(
            lambda inv: inv.journal_id.einvoice_version == '0.9')
        invoice_waiting_sign.write({
            'einvoice_state': 'waiting_sign',
            'posted_by': self.env.uid, })
        invoice_waiting_submit.write({
            'einvoice_state': 'waiting_submit',
            'posted_by': self.env.uid, })
        return res

    # pylint: disable=no-self-use
    @api.model
    def round_number(self, amount):
        """ return number in 5 digits only """
        return round(amount, 5)

    def _get_einvoice_sign(self):
        """  Get Sign if use version 0.9 """
        self.ensure_one()
        if self.journal_id.einvoice_version == '0.9':
            return {
                "signatures": [
                    {
                        "signatureType": "I",
                        "value": "MIII0QYJKoZIhvcNAQcCoIIIwjCCCL4CAQMxDTALBglg"
                                 "hkgBZQMEAgEwCwYJKoZIhvcNAQcFoIIGDzCCBgswggPz"
                                 "oAMCAQICEB7WHdVfBczn8ZiawvdzGP0wDQYJKoZIhvcNA"
                                 "QELBQAwRDELMAkGA1UEBhMCRUcxFDASBgNVBAoTC0VneX"
                                 "B0IFRydXN0MR8wHQYDVQQDExZFZ3lwdCBUcnVzdCBTZWF"
                                 "saW5nIENBMB4XDTIwMDkyODAwMDAwMFoXDTIxMDkyODIz"
                                 "NTk1OVowggFYMRgwFgYDVQRhDA9WQVRFRy02NzQ4NTk1N"
                                 "DUxIjAgBgNVBAsMGVRBWCBJRCAtIDIyNTUwMDAwODExMD"
                                 "AwMTAxJTAjBgNVBAsMHE5hdGlvbmFsIElEIC0gMjcxMDE"
                                 "xMjIxMDEzNzQxcTBvBgNVBAoMaNi02LHZg9mHINin2YTY"
                                 "tdmI2YHZiiDZhNmE2KrYrNin2LHZhyDZiNin2YTYqtmI2"
                                 "LHZitiv2KfYqiDYudio2K/Yp9mE2LnYstmK2LIg2KfYqN"
                                 "ix2KfZh9mK2YUg2KfZhNi12YjZgdmKMXEwbwYDVQQDDGj"
                                 "YtNix2YPZhyDYp9mE2LXZiNmB2Yog2YTZhNiq2KzYp9ix"
                                 "2Ycg2YjYp9mE2KrZiNix2YrYr9in2Kog2LnYqNiv2KfZh"
                                 "Ni52LLZitiyINin2KjYsdin2YfZitmFINin2YTYtdmI2Y"
                                 "HZijELMAkGA1UEBhMCRUcwggEiMA0GCSqGSIb3DQEBAQU"
                                 "AA4IBDwAwggEKAoIBAQCccO0oSnJjeL3Ebf8pL"
                                 "ON\u002Br2dUrn3o9y8pdxOLEV\u002BLcmVBYlM2fY01"
                                 "jk6vU4BLmPFoYBclwD/smbtrXvXMQeeTH\u002B/2z8VZ"
                                 "rDrsZwx3GpF5Auu0k/eruUrGN1W8LqSkMsCcIgseODTbj"
                                 "kn9tACdtFkYkrbnmqRuA9Cxc0kenscYTvtj4iUVjmJSnU"
                                 "K32c41kGQYmXyBCyfMKcxGFiF8\u002Bogg74CELrtVJf"
                                 "YA3toFGieRrD2JM\u002BziqbxfwjjtYayMHg\u002BPa"
                                 "OH06Qh/3JW/FyeQyRm3HYgxKxEGSMtPJAw/PsfqvsWOP5"
                                 "cGhgzPtsqQHyRCupLmSbYrS0dXg6/ZF1FAPyirAgMBAAG"
                                 "jgeIwgd8wCQYDVR0TBAIwADBQBgNVHR8ESTBHMEWgQ6BB"
                                 "hj9odHRwOi8vbXBraWNybC5lZ3lwdHRydXN0LmNvbS9FZ"
                                 "3lwdFRydXN0U2VhbGluZ0NBL0xhdGVzdENSTC5jcmwwCw"
                                 "YDVR0PBAQDAgbAMB0GA1UdDgQWBBSgbTpnmRnzk7m07ys"
                                 "9uTcWvVGzkDAfBgNVHSMEGDAWgBS15KC43nSgLTbHhRp"
                                 "k/f8aINUKwzARBglghkgBhvhCAQEEBAMCB4AwIAYDVR0R"
                                 "BBkwF4EVZXllaGlhQGVneXB0dHJ1c3QuY29tMA0GCSqGS"
                                 "Ib3DQEBCwUAA4ICAQC7wmdpRtWiIuQsokfjUl3pruOsX"
                                 "7NBU46h\u002B\u002BWReQR/ceEcdzDRBVqwM7FKsTZ"
                                 "y3/i6ACSE9MUMpMUPgtR\u002BneBq1cuknFSqhgQmnOa"
                                 "8mG2/nUjISNhyrcrnFSYrmJyBxT2wOO8xwtLDA2PQJId"
                                 "G/n1Xn6YxwU7gbB0NApPmORhMfD1S6KINzvTj1D/EIpMa"
                                 "Kzg7DC4wYgR2UbO8dFvNgaNtze/GRks7xQC4KMJ9udaf0"
                                 "JBOzyvuGtjzsB\u002B69XG0t68WVXyTIqxBZKVVU4jqG"
                                 "9JZdKhCHgr2P2G4nEJxTiXf3cl6iemdC1JezaoGW5FEp"
                                 "h/wFqswiP05TVQdLOB9EkurvdrBF6sY8Xbk/2st5FvG9u"
                                 "AUuyQjzUETA/As4Clqr9dNirT6OVzWhI06S8CTgOONXwW"
                                 "Tx9CjCoc\u002BERx8ce20YgVipZnKfz2MRy3bCF3"
                                 "7\u002BCOgNyPNXy/bneFlSKEpMPYUKk5jt2z3G/I9gyo"
                                 "zaXVGZ3sFjxHu0UX5fuiP7xknmPDdSi\u002BMwEfnh8E"
                                 "ApgSvPlY7RLWQU8A2cUqWrCOvvuQfc2C5VG8CB"
                                 "P\u002BldOZt54OXSfEnx2841bTyKJGP86NvAZOTN9wF"
                                 "KoyhBztN9FmhG69IWbtsxdit2pbgCofh751MsN1Zbp9Je"
                                 "rLwBxrmcEmUZfwSvE8ojOipxaszLKzg1SO7QTGCAogwg"
                                 "gKEAgEBMFgwRDELMAkGA1UEBhMCRUcxFDASBgNVBAoTC0"
                                 "VneXB0IFRydXN0MR8wHQYDVQQDExZFZ3lwdCBUcnVzdCB"
                                 "TZWFsaW5nIENBAhAe1h3VXwXM5/GYmsL3cxj9MAsGCWCG"
                                 "SAFlAwQCAaCCAQUwGAYJKoZIhvcNAQkDMQsGCSqGSIb3D"
                                 "QEHBTAcBgkqhkiG9w0BCQUxDxcNMjAxMTAzMTAwMTQ4Wj"
                                 "AvBgkqhkiG9w0BCQQxIgQgUt/GoPN5xkeHpV4L5olwuic"
                                 "aAObCbf0ORKgN4O260CIwgZkGCyqGSIb3DQEJEAIvMYGJ"
                                 "MIGGMIGDMIGABCD6bb7asgHoS/gNVKpFneOpR/9uWobTY"
                                 "wah5r9IQzH\u002BcTBcMEigRjBEMQswCQYDVQQGEwJFR"
                                 "zEUMBIGA1UEChMLRWd5cHQgVHJ1c3QxHzAdBgNVBAMTFk"
                                 "VneXB0IFRydXN0IFNlYWxpbmcgQ0ECEB7WHdVfBczn8Zi"
                                 "awvdzGP0wCwYJKoZIhvcNAQEBBIIBAC3gpQ0ldw5TCYHG"
                                 "0rNMGveNtoC2vRWk7EXjPCYQJS11fkBnZ6VWAgcFtJrBH"
                                 "zv0x81Ik6ngvXlrl/bmB0yCm71yLcL4iBFRvB1CQ8nBln"
                                 "rx24xD2OQPC\u002Bjza/7yt/y747kaJgoOcmP5Q7k92v"
                                 "tnIxdO\u002BX0SI3Jb9\u002BuByvJEZZTFHnjXie4gK"
                                 "LyR2HZqHB2VLf/scBTe2\u002BzxQx3p3Hn15Sh7Muufw"
                                 "0ARpZkuiT5haskusdGRF2JEsHtGX/X57JmXzHdOms/mDu"
                                 "sbg4Mee2tLT\u002B67Bnz8FAX8qTMD8oCtOdfQaKQDhy"
                                 "yCsqxeLUMJ5oM28ZA/Ncf\u002BMlmVl0\u002BHKkGS1"
                                 "3c="
                    }
                ]
            }
        return {
            "signatures": [
                {
                    "signatureType": "I",
                    "value": self.einvoice_signature
                }
            ]
        }

    # pylint: disable=too-many-locals
    def prepare_invoice_json(self, signed=True, documents_object=True):
        """ get json structure used to send to e-invoice """
        company = self.env.company
        documents = []
        for move in self:
            partner = move.partner_id
            partner_bank = move.partner_bank_id
            invoice_lines = move.invoice_line_ids.einvoice_data()
            total_untaxed = sum(
                map(lambda r: r.get('salesTotal'), invoice_lines))
            total_included = sum(map(lambda r: r.get('total'), invoice_lines))
            total_nontaxable = sum(
                map(lambda r: r.get('itemsDiscount'), invoice_lines))
            document_type = DOCUMENT_TYPE[move.move_type]
            if move.debit_origin_id:
                document_type = 'D'
            po_ref = move.ref
            if document_type == 'C':
                po_ref = False
            elif document_type == 'D':
                po_ref = False
            # @formatter:off
            tax_groups = []
            for line in invoice_lines:
                taxable_items = line.get('taxableItems', [])
                for taxable_item in taxable_items:
                    tax_type = taxable_item.get('taxType')
                    tax_amount = taxable_item.get('amount')
                    if not tax_groups:
                        tax_groups.append({
                            'taxType': tax_type,
                            'amount': tax_amount,
                        })
                    else:
                        list_of_tax_types_added = set([d.get('taxType', None) for d in tax_groups])
                        if tax_type not in list_of_tax_types_added:
                            tax_groups.append({
                                    'taxType': tax_type,
                                    'amount': tax_amount,
                                })
                        else:
                            for tax_group in tax_groups:
                                if tax_group.get('taxType') == tax_type:
                                    amount = tax_group.get('amount')
                                    tax_group.update({'amount': amount + tax_amount})

            document = {
                "issuer": company.einvoice_data(),
                "receiver": partner.einvoice_data(),
                "documentType": document_type,
                "documentTypeVersion": move.journal_id.einvoice_version,
                "dateTimeIssued":
                    datetime.combine(move.invoice_date, datetime.min.time()
                                     ).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "taxpayerActivityCode": company.invoice_activity_type_id.code,
                "internalID": move.name,
                "purchaseOrderReference": po_ref or "",
                "purchaseOrderDescription": "",
                "salesOrderReference": move.invoice_origin or "",
                "salesOrderDescription": "",
                "proformaInvoiceNumber": "",
                "payment": {
                    "bankName": partner_bank.bank_id.name or "",
                    "bankAddress": "%s  %s %s %s %s" % (
                        partner_bank.bank_id.street or '',
                        partner_bank.bank_id.street2 or '',
                        partner_bank.bank_id.city or '',
                        partner_bank.bank_id.state.name or '',
                        partner_bank.bank_id.country.name or ''),
                    "bankAccountNo": partner_bank.acc_number or "",
                    "bankAccountIBAN": partner_bank.iban or "",
                    "swiftCode": partner_bank.bank_id.bic or "",
                    "terms": move.invoice_payment_term_id.name or ""
                },
                "invoiceLines": invoice_lines,
                "totalSalesAmount": self.round_number(total_untaxed),
                "netAmount": self.round_number(total_untaxed),
                "taxTotals": tax_groups,
                "totalAmount": self.round_number(total_included),
                "extraDiscountAmount": 0.0,
                "totalDiscountAmount": 0.0,
                "totalItemsDiscountAmount": self.round_number(total_nontaxable),
            }
            # @formatter:on
            if signed:
                # pylint: disable=protected-access
                document.update(move._get_einvoice_sign())
            documents.append(document)
        data = documents
        if documents_object:
            data = {"documents": documents}
        return json.dumps(data, ensure_ascii=False)

    def submit_document(self):
        """ create request to send documents to e-invoice """
        einvoice_outgoing_obj = self.env['account.einvoice.outgoing']
        for move in self:
            if move.move_type in ['out_invoice', 'out_refund', 'out_receipt'] \
                    and move.journal_id.submit_einvoice:
                if move.journal_id.einvoice_version == '1.0' \
                        and not move.einvoice_signature:
                    raise \
                        ValidationError(_('Please sign invoice before submit'))
                access_token = einvoice_outgoing_obj.login_as_taxpayer_system(
                    move.journal_id)
                url = SYSTEM_API[move.journal_id.einvoice_purpose]
                data = move.prepare_invoice_json()
                headers = {
                    "Content-Type": "application/json",
                    "authorization": "Bearer %s" % access_token
                }
                submit_request_id = einvoice_outgoing_obj.sudo().create({
                    'move_ids': move.ids,
                    'method': 'post',
                    'request_url': '%s/api/v1/documentsubmissions' % url,
                    'request_header': headers,
                    'request_data': data,
                    'action_type': 'submit',
                })
                move.einvoice_state = 'in_queue'
                if self.env.context.get('force_submit'):
                    submit_request_id.sudo().action_submit()

    @api.model
    def _auto_submit(self):
        """ This method is called from a cron job.
        It is used to submit invoices.
        """
        records = self.search(
            [('move_type', 'in', ['out_invoice', 'out_refund', 'out_receipt']),
             ('einvoice_state', '=', 'waiting_submit')])
        records.submit_document()

    def get_einvoice_printout(self):
        """ allow to print E-Invoice PDF """
        einvoice_outgoing_obj = self.env['account.einvoice.outgoing']
        for move in self:
            move.action_update_einvoice_status()
            if move.einvoice_uuid and \
                    move.einvoice_state in \
                    ['submitted', 'valid', 'rejected', 'cancelled',
                     'waiting_cancel']:
                access_token = einvoice_outgoing_obj.login_as_taxpayer_system(
                    move.journal_id)
                headers = {
                    "Content-Type": "application/juson",
                    "Accept-Language": move.commercial_partner_id.lang,
                    "authorization": "Bearer %s" % access_token
                }
                url = SYSTEM_API[move.journal_id.einvoice_purpose]
                printout_outgoing = einvoice_outgoing_obj.sudo().create({
                    'move_ids': move.ids,
                    'method': 'get',
                    'request_url': '%s/api/v1.0/documents/%s/pdf' %
                                   (url, move.einvoice_uuid),
                    'request_header': headers,
                    'action_type': 'printout',
                })
                printout_outgoing.action_printout()

    def _prepare_cancel_einvoice(self, cancel_reason="Other"):
        """" prepare data"""
        self.ensure_one()
        return json.dumps({"status": "cancelled", "reason": cancel_reason})

    def action_cancel_einvoice(self):
        """ submit cancel to e-invoice """
        einvoice_outgoing_obj = self.env['account.einvoice.outgoing']
        for move in self:
            access_token = einvoice_outgoing_obj.login_as_taxpayer_system(
                move.journal_id)
            url = SYSTEM_API[move.journal_id.einvoice_purpose]
            cancel_reason = move.cancel_reason_id.name
            if cancel_reason:
                data = move._prepare_cancel_einvoice(cancel_reason)
            else:
                data = move._prepare_cancel_einvoice()
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer %s" % access_token}
            cancel_request_id = einvoice_outgoing_obj.sudo().create({
                'move_ids': move.ids,
                'method': 'put',
                'request_url': '%s/api/v1.0/documents/state/%s/state' %
                               (url, move.einvoice_uuid),
                'request_header': headers,
                'request_data': data,
                'action_type': 'cancel',
            })
            cancel_request_id.action_cancel()

    # pylint: disable=too-many-nested-blocks
    def action_update_einvoice_status(self):
        """ update einvoice status from ETA """
        for move in self:
            if move.einvoice_uuid:
                einvoice_json = \
                    self._get_einvoice_info(move)
                if einvoice_json:
                    einvoice_state = einvoice_json.get("status").lower()
                    if einvoice_json.get("cancelRequestDate") and \
                            einvoice_state == "valid":
                        einvoice_state = "waiting_cancel"
                    move.einvoice_state = einvoice_state
                    msg = ""
                    if einvoice_state == "invalid":
                        validation_results = einvoice_json.get(
                            "validationResults", [])
                        validation_steps = \
                            validation_results.get("validationSteps", [])
                        for step in validation_steps:
                            if step.get('error'):
                                msg += '\n'.join([
                                    f"{detail.get('errorCode')}:"
                                    f" {detail.get('error')}"
                                    for detail in
                                    step.get('error', {}).get('innerError', [])
                                ])
                    move.einvoice_message = msg if msg else False

    def _get_einvoice_info(self, move=False, **kwargs):
        """ get invoice details from ETA
        :type move: object
        """
        journal = kwargs.get("journal", False)
        einvoice_uuid = kwargs.get("einvoice_uuid", False)
        if move:
            journal = move.journal_id
            einvoice_uuid = move.einvoice_uuid
        einvoice_outgoing_obj = self.env['account.einvoice.outgoing']
        access_token = einvoice_outgoing_obj.login_as_taxpayer_system(journal)
        url = SYSTEM_API[journal.einvoice_purpose]
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer %s" % access_token}
        get_detail_request_id = einvoice_outgoing_obj.sudo().create({
            'move_ids': move.ids if move else False,
            'method': 'get',
            'request_url':
                '%s/api/v1.0/documents/%s/details' % (url, einvoice_uuid),
            'request_header': headers,
            'action_type': 'get_detail',
        })
        return get_detail_request_id.action_get_details()
