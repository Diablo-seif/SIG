""" Initialize Proposal Activity Report """

from odoo import fields, models, tools


class ProposalActivityReport(models.Model):
    """ Proposal Activity Report """

    _name = "proposal.activity.report"
    _auto = False
    _description = "Proposal Activity Report"
    _rec_name = 'id'

    date = fields.Datetime('Completion Date', readonly=True)
    proposal_create_date = fields.Datetime('Creation Date', readonly=True)
    date_order = fields.Date('Conversion Date', readonly=True)
    author_id = fields.Many2one('res.partner', 'Assigned To', readonly=True)
    user_id = fields.Many2one('res.users', 'Salesperson', readonly=True)
    proposal_id = fields.Many2one('proposal.proposal', "Proposal", readonly=True)
    body = fields.Html('Activity Description', readonly=True)
    subtype_id = fields.Many2one('mail.message.subtype', 'Subtype',
                                 readonly=True)
    mail_activity_type_id = fields.Many2one('mail.activity.type',
                                            'Activity Type', readonly=True)
    partner_id = fields.Many2one('res.partner', readonly=True)
    active = fields.Boolean('Active', readonly=True)

    def _select(self):
        return """
            SELECT
                m.id,
                p.create_date AS proposal_create_date,
                p.date_order,
                p.id as proposal_id,
                p.activity_user_id AS user_id,
                p.partner_id,
                p.active,
                m.subtype_id,
                m.mail_activity_type_id,
                m.author_id,
                m.date,
                m.body
        """

    def _from(self):
        return """
            FROM mail_message AS m
        """

    def _join(self):
        return """
            JOIN proposal_proposal AS p ON m.res_id = p.id
        """

    def _where(self):
        disccusion_subtype = self.env.ref('mail.mt_comment')
        return """
            WHERE
                m.model = 'proposal.proposal' AND (m.mail_activity_type_id IS NOT NULL OR m.subtype_id = %s)
        """ % (disccusion_subtype.id,)

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                %s
                %s
                %s
                %s
            )
        """ % (
            self._table, self._select(), self._from(), self._join(),
            self._where())
                         )
