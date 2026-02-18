""" inherit Approval Category to add wide usage """

from ast import literal_eval

from odoo import api, fields, models


# pylint: disable=protected-access,inconsistent-return-statements,no-member
# pylint: disable=fixme
class ApprovalCategory(models.Model):
    """ inherit Approval Category"""
    _inherit = 'approval.category'

    model_id = fields.Many2one('ir.model', string='Model Approval')
    model = fields.Char(related='model_id.model')
    action_id = fields.Many2one('ir.actions.act_window')
    domain = fields.Char()
    context = fields.Char(default='{}')

    @api.onchange('model_id')
    def _onchange_model_id(self):
        """ reset and add domain to action_id to filter model actions """
        self.action_id = False
        if self.model_id:
            return {'domain': {
                'action_id': [('res_model', '=', self.model_id.model)]
            }}

    def validate_domain(self, domain):
        """
            Validate Domain
            :param domain:
            :return: domain with x_approval_category_id extra condition
        """
        self.ensure_one()
        domain = literal_eval(domain or '[]')
        domain.append(('x_approval_category_id', '=', self.id))
        return domain

    def validate_context(self, context):
        """
            Validate Domain
            :param context:
            :return: context with default_x_approval_category_id extra key
        """
        self.ensure_one()
        # context in string format, i'm trying to add extra ctx
        ctx = context.replace('{', '').replace('}', '')
        ctx = u"{'default_x_approval_category_id': %s,%s}" % (str(self.id), ctx)
        return ctx

    def create_request(self):
        """ inherit create_request() """
        self.ensure_one()
        if self.action_id and self.model_id:
            action = self.action_id.sudo().read()[0]
            action['context'] = self.validate_context(self.context)
            action['views'] = [(False, 'form')]
            # FIXME: for some reason some actions will raise errors
            return action
        return super().create_request()

    def view_request(self):
        """
         return action in tree view with the filtered
         record set by the domain in the category
        """
        self.ensure_one()
        action = self.env.ref(
            'approvals.approval_request_action_to_review_category'
        ).sudo().read()[0]
        if self.action_id and self.model_id:
            action = self.action_id.sudo().read()[0]
            action['domain'] = self.validate_domain(self.domain)
            action['context'] = self.validate_context(self.context)
            action['views'] = [(False, 'list'), (False, 'form')]
        return action

    # pylint: disable=missing-return
    def _compute_request_to_validate_count(self):
        """ inherit _compute_request_to_validate_count() """
        for category in self:
            if category.action_id and category.model_id:
                category.request_to_validate_count = \
                    self.env[category.model_id.model].search_count(
                        category.validate_domain(category.domain))
            else:
                super()._compute_request_to_validate_count()
