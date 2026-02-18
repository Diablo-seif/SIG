""" HR Course Provider line """

from odoo import _, api, fields, models


class HrCourseProviderLine(models.Model):
    """HR Course Type """
    _name = "hr.course.provider.line"
    _description = 'Course Provider'
    _sql_constraints = [(
        'minimum_no_of_participants',
        'CHECK ((minimum_no_of_participants >= 0 ))',
        _('Minimum number of participants must be greater than 0')
    ), (
        'cost_per_participant',
        'CHECK ((cost_per_participant >= 0 ))',
        _('Cost per participant must be greater than 0')
    )]

    partner_id = fields.Many2one(
        "res.partner",
        string="Service Provider"
    )
    course_id = fields.Many2one(
        "hr.course"
    )
    minimum_no_of_participants = fields.Integer()
    cost_per_participant = fields.Monetary()
    certification_id = fields.Many2one(
        'hr.resume.line.type'
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id.id
    )
    provider_type = fields.Selection(
        [("internal", "Internal"),
         ("external", "External")],
        default="internal"
    )

    @api.onchange('provider_type')
    def _onchange_provider_type(self):
        """ Add domain to some filed """
        self.partner_id = False
        if self.provider_type == 'internal':
            domain = [('user_ids', '!=', False)]
        else:
            domain = [('user_ids', '=', False)]
        return {'domain': {'partner_id': domain}}

    def name_get(self):
        """ Override name_get to change displayed name """
        return [(
            rec.id,
            _("%(partner_name)s/%(provider_type)s/%(cost_per_participant)"
              "s%(currency_symbol)s") % {
                  "partner_name": rec.partner_id.name,
                  "provider_type": dict(self.fields_get(
                      allfields=['provider_type'])['provider_type']['selection']
                                       )[rec.provider_type],
                  "cost_per_participant": rec.cost_per_participant,
                  "currency_symbol": rec.currency_id.symbol,
              }
        ) for rec in self]
