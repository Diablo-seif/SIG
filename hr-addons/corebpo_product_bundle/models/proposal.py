
from odoo import models, fields, api


class Proposal(models.Model):
    _inherit = 'proposal.proposal'

    bundle_product_ids = fields.Many2many(
        'product.template', domain="[('sh_is_bundle', '=', True)]")

    
    @api.onchange('bundle_product_ids')
    def _onchange_bundle_product_ids(self):
    
        self.line_ids = [(5,0,0)]

        for bundle_product in self.bundle_product_ids:
            for sh_bundle_product in bundle_product.sh_bundle_product_ids:
                self.line_ids = [(0, 0,  
                {'product_id': sh_bundle_product.sh_product_id.id, 
                 'product_uom_qty': sh_bundle_product.sh_qty,
                #  'unit_price': sh_bundle_product.sh_price_unit,
                 'name': sh_bundle_product.sh_product_id.description_sale,
                 'unit_cost': sh_bundle_product.sh_cost_price,
                 'uom_id': sh_bundle_product.sh_uom.id,
                })]
            
            