""" Initialize Res Company """

import re

from odoo import fields, models


# pylint: disable=no-member
class ResCompany(models.Model):
    """
        Inherit Res Company:
    """
    _inherit = 'res.company'

    invoice_activity_type_id = fields.Many2one('invoice.activity.type')
    building_number = fields.Char()

    def get_einvoice_vat(self):
        """
        get partner vat
        can be override to apply any value
        """
        return self.vat

    def einvoice_data(self):
        """  Einvoice Issuer """
        self.ensure_one()
        # @formatter:off
        return {
            "address": {
                "branchID": "0",
                "country": self.country_id.code,
                "governate": self.state_id.name,
                "regionCity": self.city,
                "street": '%s %s' % (self.street or '', self.street2 or ''),
                "buildingNumber": self.building_number,
                "postalCode": self.zip or '',
            },
            "type": "B",
            "id": ''.join(re.findall('[0-9]+', self.vat)),
            "name": self.name
        }
