"""Integrated Tests TestFiscalPosition"""

from odoo.tests.common import TransactionCase
from odoo import fields


class TestFiscalPosition(TransactionCase):
    """Integrated Tests new map_tax"""

    def setUp(self):
        """Setup the testing environment."""
        super(TestFiscalPosition, self).setUp()
        self.fiscal = self.env['account.fiscal.position']

        # reset any existing FP
        self.fiscal.search([]).write({'auto_apply': False})

    # pylint: disable=no-member, attribute-defined-outside-init
    def test_01_fp_one_tax_2m(self):
        """test Scenario: Create Object. """
        self.src_tax = self.env['account.tax'].create(
            {'name': "SRC", 'amount': 0.0})
        self.dst1_tax = self.env['account.tax'].create(
            {'name': "DST1", 'amount': 0.0})
        self.dst2_tax = self.env['account.tax'].create(
            {'name': "DST2", 'amount': 0.0})

        self.fiscal_id = self.fiscal.create({
            'name': "FP-TAX2TAXES",
            'tax_ids': [
                (0, 0, {
                    'tax_src_id': self.src_tax.id,
                    'tax_dest_id': self.dst1_tax.id
                }),
                (0, 0, {
                    'tax_src_id': self.src_tax.id,
                    'tax_dest_id': self.dst2_tax.id
                })
            ]
        })
        mapped_taxes = self.fiscal_id.map_tax(self.src_tax)
        self.fiscal_id.map_tax(self.src_tax, date=fields.Date.today())
        self.assertEqual(mapped_taxes, self.dst1_tax | self.dst2_tax)
