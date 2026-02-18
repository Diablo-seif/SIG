""" Initialize Res Partner """

import re

from odoo import fields, models


# pylint: disable=no-member
class ResPartner(models.Model):
    """
        Inherit Res Partner:
    """
    _inherit = 'res.partner'

    receiver_type = fields.Selection(
        [('B', 'Business In Egypt'), ('P', 'Natural Person'),
         ('F', 'Foreigner')])
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
        vat = self.get_einvoice_vat()
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
            "type": self.receiver_type,
            "id": ''.join(re.findall('[0-9]+', vat))
                  if self.receiver_type not in ['F', 'P'] else vat or "",
            "name": self.name
        }
