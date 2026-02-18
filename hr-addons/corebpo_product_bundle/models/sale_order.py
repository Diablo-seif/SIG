
from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    bundle_product_ids = fields.Many2many(
        'product.template', domain="[('sh_is_bundle', '=', True)]")

    
    @api.onchange('bundle_product_ids')
    def _onchange_bundle_product_ids(self):
    
        self.order_line = [(5,0,0)]

        for bundle_product in self.bundle_product_ids:
            for sh_bundle_product in bundle_product.sh_bundle_product_ids:
                self.order_line = [(0, 0,  
                {'product_id': sh_bundle_product.sh_product_id.id, 
                 'product_uom_qty': sh_bundle_product.sh_qty,
                 'price_unit': sh_bundle_product.sh_price_unit
                })]
            
            