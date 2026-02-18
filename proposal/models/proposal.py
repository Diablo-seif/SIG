"""Initialize Proposal"""

import base64

from dateutil.relativedelta import relativedelta
from datetime import datetime, date

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Proposal(models.Model):
    """
    Initialize Proposal:
     -
    """

    _name = "proposal.proposal"
    _description = "Proposals"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _check_company_auto = True

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("sent_to_purchase", "Sent To Purchase"),
            ("sent_to_sales", "Sent To Sales"),
            ("done", "Won"),
            ("cancelled", "Cancelled"),
            ("lost", "Lost"),
        ],
        default="draft",
        string="Status",
        tracking=True,
    )
    stage_id = fields.Many2one(
        "proposal.stage",
        default=lambda self: self.env["proposal.stage"].search(
            [("is_draft", "=", True)], limit=1, order="sequence"
        ),
        group_expand="_group_expand_stage_id",
        tracking=True,
        compute="_compute_stage",
        store=True,
    )
    lost_reason_id = fields.Many2one("proposal.lost.reason", tracking=True)
    name = fields.Char(default=_("New"), translate=True, copy=False)
    active = fields.Boolean(default=True, tracking=True)
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
    )
    partner_id = fields.Many2one("res.partner", required=True)
    analytic_account_id = fields.Many2one("account.analytic.account", required=True)
    date_order = fields.Date(default=fields.Date.today(), string="Proposal Date")
    line_ids = fields.One2many("proposal.line", "proposal_id", tracking=True)
    purchase_ids = fields.One2many("purchase.order", "proposal_id")
    purchase_responsible_id = fields.Many2one(
        "res.users",
    )
    actual_revenue = fields.Monetary(
        compute="_compute_actual_revenue", store=True, compute_sudo=True
    )
    actual_cost = fields.Monetary(
        compute="_compute_actual_cost", store=True, compute_sudo=True
    )
    sale_ids = fields.One2many("sale.order", "proposal_id")
    sale_id = fields.Many2one(
        "sale.order",
    )
    expected_revenue = fields.Monetary(
        compute="_compute_expected_revenue",
        store=True,
    )
    expected_cost = fields.Monetary(
        compute="_compute_expected_cost",
        store=True,
    )
    expected_margin = fields.Monetary(
        compute="_compute_expected_margin",
        store=True,
    )
    expected_margin_percentage = fields.Float(
        compute="_compute_expected_margin",
        store=True,
    )
    amendment_revenue = fields.Monetary(
        compute="_compute_amendment_revenue",
        store=True,
    )
    amendment_cost = fields.Monetary(
        compute="_compute_amendment_cost",
        store=True,
    )
    amendment_margin = fields.Monetary(
        compute="_compute_amendment_margin",
        store=True,
    )
    amendment_margin_percentage = fields.Float(
        compute="_compute_amendment_margin",
        store=True,
    )
    contracted_revenue = fields.Monetary(
        compute="_compute_contracted_revenue",
        store=True,
    )
    contracted_cost = fields.Monetary(
        compute="_compute_contracted_cost",
        store=True,
    )
    contracted_margin = fields.Monetary(
        compute="_compute_contracted_margin",
        store=True,
    )
    contracted_margin_percentage = fields.Float(
        compute="_compute_contracted_margin",
        store=True,
    )
    actual_margin = fields.Monetary(compute="_compute_actual_margin", store=True)
    actual_margin_percentage = fields.Float(
        compute="_compute_actual_margin", store=True
    )
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id
    )
    margin_type = fields.Selection(
        [("percentage", "Percentage"), ("amount", "Amount")],
        default="percentage",
    )
    margin_percentage = fields.Float()
    margin_amount = fields.Float(
        compute="_compute_margin_amount", inverse="_inverse_margin_amount", store=True
    )
    sequence_id = fields.Many2one(
        "ir.sequence",
    )
    claim_sequence_id = fields.Many2one(
        "ir.sequence",
    )
    current_version = fields.Char()
    activity_user_id = fields.Many2one(store=True)
    claim_ids = fields.One2many("proposal.claim", "proposal_id")
    financial_progress = fields.Float(compute="_compute_progress", store=True)
    project_progress = fields.Float(compute="_compute_progress", store=True)
    project_id = fields.Many2one("project.project")
    move_ids = fields.One2many("account.move", "proposal_id")
    tag_id = fields.Many2one(
        "proposal.tag",
        string="Main Tag",
        # compute='_compute_tag_id',
        # inverse='_inverse_tag_id',
        # store=True,
        # readonly=False,
        # check_company=True
    )
    tag_ids = fields.Many2many("proposal.tag", string="Tags", check_company=True)
    is_outsourcing = fields.Boolean(related="tag_id.is_outsourcing")
    proposal_yearly_financial_ids = fields.One2many(
        "proposal.yearly.financial",
        "proposal_id",
        compute="_compute_proposal_yearly_financial_ids",
        store=True,
    )
    contract_date = fields.Date()

    @api.depends("move_ids", "move_ids.amount_untaxed", "move_ids.state")
    def _compute_proposal_yearly_financial_ids(self):
        for rec in self:
            existing_records = self.env["proposal.yearly.financial"].search(
                [("proposal_id", "=", rec.id)]
            )
            existing_records.unlink()

            date_order = rec.date_order
            today_date = datetime.today()
            years = list(range(date_order.year, today_date.year + 1))
            for year in years:
                start_date = date(year, 1, 1)
                end_date = date(year, 12, 31)
                moves = rec.move_ids.filtered(lambda r: r.date <= end_date)

                actual_year_revenue = sum(
                    moves.filtered(
                        lambda r: r.date <= end_date
                        and r.state == "posted"
                        and r.move_type == "out_invoice"
                    ).mapped("amount_untaxed")
                )

                actual_year_cost = 0
                for move in moves:
                    if move.state == "posted" and (
                        move.move_type == "entry" or move.move_type == "in_invoice"
                    ):
                        for line in move.line_ids:
                            if (
                                line.account_id.account_type == "expense"
                                or line.account_id.account_type == "expense_direct_cost"
                            ):
                                actual_year_cost += line.debit - line.credit

                if start_date <= rec.date_order <= end_date:
                    type = "new"
                else:
                    type = "old"

                remaining_revenue = rec.contracted_revenue - actual_year_revenue
                remaining_cost = rec.contracted_cost - actual_year_cost

                if type == "new" or remaining_revenue > 0 or remaining_cost > 0:
                    cumulative_remaining_revenue = sum(
                        self.env["proposal.yearly.financial"]
                        .search([("proposal_id", "=", rec.id), ("year", "<", year)])
                        .mapped("remaining_revenue")
                    )
                    cumulative_remaining_cost = sum(
                        self.env["proposal.yearly.financial"]
                        .search([("proposal_id", "=", rec.id), ("year", "<", year)])
                        .mapped("remaining_cost")
                    )

                    self.env["proposal.yearly.financial"].sudo().create(
                        {
                            "proposal_id": rec.id,
                            "year": year,
                            "type": type,
                            "remaining_revenue": remaining_revenue,
                            "remaining_cost": remaining_cost,
                            "cumulative_remaining_revenue": cumulative_remaining_revenue,
                            "cumulative_remaining_cost": cumulative_remaining_cost,
                            # 'remaining_margin': rec.actual_margin - (actual_year_revenue - actual_year_cost),
                        }
                    )
            rec.proposal_yearly_financial_ids = self.env[
                "proposal.yearly.financial"
            ].search([("proposal_id", "=", rec.id)])

    # @api.depends('tag_ids')
    # def _compute_tag_id(self):
    #     """ Compute tag_id value """
    #     for rec in self:
    #         rec.tag_id = rec.tag_ids and rec.tag_ids[0].id or rec.tag_id.id

    # @api.onchange('tag_id')
    # def _inverse_tag_id(self):
    #     """ Inverse _tag_id value """
    #     for rec in self:
    #         if rec.tag_id.id:
    #             tags = [rec.tag_id.id] + rec.tag_ids.ids
    #         else:
    #             tags = rec.tag_ids.ids
    #         rec.tag_ids = [(5,)]
    #         rec.tag_ids = tags

    def action_view_invoices(self):
        """:return Account Move action"""
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "name": _("Invoices"),
            "view_mode": "list,form",
            "domain": [
                ("proposal_id", "=", self.id),
                ("move_type", "=", "out_invoice"),
            ],
            "views": [(False, "list"), (False, "form")],
        }

    def action_view_bills(self):
        """:return Account Move action"""
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "name": _("Bills"),
            "view_mode": "list,form",
            "domain": [("proposal_id", "=", self.id), ("move_type", "=", "in_invoice")],
            "context": {
                "default_proposal_id": self.id,
                "default_move_type": "in_invoice",
            },
            "views": [(False, "list"), (False, "form")],
        }

    def action_view_entries(self):
        """:return Account Move action"""
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "name": _("Entries"),
            "view_mode": "list,form",
            "domain": [("proposal_id", "=", self.id), ("move_type", "=", "entry")],
            "context": {"default_proposal_id": self.id, "default_move_type": "entry"},
            "views": [(False, "list"), (False, "form")],
        }

    @api.depends(
        "expected_revenue", "line_ids.total_claimed_amount", "project_id.progress"
    )
    def _compute_progress(self):
        """Compute progress value"""
        for rec in self:
            rec.financial_progress = (
                rec.expected_revenue
                and sum(
                    rec.line_ids.filtered(lambda r: r.display_type == False).mapped(
                        "total_claimed_amount"
                    )
                )
                / rec.expected_revenue
                or 0
            )
            rec.project_progress = rec.project_id.progress

    def do_version(self):
        """increment version"""
        for rec in self:
            if not rec.sequence_id:
                rec._create_sequence()
            rec.current_version = rec.name + rec.sequence_id._next()

    def _create_sequence(self):
        """Create Sequence"""
        for rec in self:
            if not rec.sequence_id:
                rec.sequence_id = (
                    self.env["ir.sequence"]
                    .sudo()
                    .create(
                        {
                            "name": f"{rec.name} versions",
                            "code": rec.name,
                            "prefix": "/",
                            "padding": 2,
                            "number_next": 1,
                            "number_increment": 1,
                            "company_id": False,
                        }
                    )
                )

    def _create_claim_sequence(self):
        """Create Sequence"""
        for rec in self:
            if not rec.claim_sequence_id:
                rec.claim_sequence_id = (
                    self.env["ir.sequence"]
                    .sudo()
                    .create(
                        {
                            "name": f"{rec.name} claim",
                            "code": f"{rec.name}.claim",
                            "prefix": "/CLM/",
                            "padding": 2,
                            "number_next": 1,
                            "number_increment": 1,
                            "company_id": False,
                        }
                    )
                )

    @api.depends("state")
    def _compute_stage(self):
        for record in self:
            # field = 'is_' + record.state
            field = f"is_{record.state or 'draft'}".strip()
            stage = (
                self.env["proposal.stage"].sudo().search([(field, "=", True)], limit=1)
            )
            if stage.id:
                record.stage_id = stage.id
            else:
                record.stage_id = False

    def action_print_proposal(self):
        self.do_version()
        return self.env.ref("proposal.proposal_report").report_action(self)

    @api.depends("expected_cost", "margin_percentage")
    def _compute_margin_amount(self):
        """Compute margin_amount value"""
        for rec in self:
            rec.margin_amount = (
                rec.expected_cost / (1 - rec.margin_percentage)
            ) - rec.expected_cost

    @api.onchange("expected_cost", "margin_amount")
    def _inverse_margin_amount(self):
        """Compute margin_amount value"""
        for rec in self:
            margin_percentage = (
                (-rec.expected_cost - rec.margin_amount)
                and -rec.margin_amount / (-rec.expected_cost - rec.margin_amount)
                or 0
            )
            rec.margin_percentage = margin_percentage
            rec.line_ids.filtered(
                lambda r: r.display_type == False
            ).margin_percentage = margin_percentage

    @api.depends("move_ids.amount_untaxed", "move_ids.state")
    def _compute_actual_cost(self):
        """Compute expected_cost value"""
        for rec in self:
            # rec.actual_cost = sum(rec.move_ids.filtered(
            #     lambda
            #         r: r.state == 'posted' and
            #         (r.move_type == 'entry' or r.move_type == "in_invoice")).mapped(
            #     'amount_total'))
            rec.actual_cost = 0
            for move in rec.move_ids:
                if move.state == "posted" and (
                    move.move_type == "entry" or move.move_type == "in_invoice"
                ):
                    for line in move.line_ids:
                        if (
                            line.account_id.account_type == "expense"
                            or line.account_id.account_type == "expense_direct_cost"
                        ):
                            rec.actual_cost += line.debit - line.credit

    @api.depends("move_ids.amount_untaxed", "move_ids.state")
    def _compute_actual_revenue(self):
        """Compute expected_revenue value"""
        for rec in self:
            rec.actual_revenue = sum(
                rec.move_ids.filtered(
                    lambda r: r.state == "posted" and r.move_type == "out_invoice"
                ).mapped("amount_untaxed")
            )

    @api.depends("line_ids.cost", "line_ids.amendment")
    def _compute_expected_cost(self):
        """Compute expected_cost value"""
        for rec in self:
            rec.expected_cost = sum(
                rec.line_ids.filtered(
                    lambda r: r.display_type == False and not r.amendment
                ).mapped("cost")
            )

    @api.depends("line_ids.price", "line_ids.amendment")
    def _compute_expected_revenue(self):
        """Compute expected_revenue value"""
        for rec in self:
            rec.expected_revenue = sum(
                rec.line_ids.filtered(
                    lambda r: r.display_type == False and not r.amendment
                ).mapped("price")
            )

    @api.depends("expected_revenue", "expected_cost")
    def _compute_expected_margin(self):
        """Compute expected_margin value"""
        for rec in self:
            expected_margin = rec.expected_revenue - rec.expected_cost
            rec.expected_margin = expected_margin
            rec.expected_margin_percentage = (
                rec.expected_revenue and expected_margin / rec.expected_revenue or 0
            )

    @api.depends("line_ids.cost", "line_ids.amendment")
    def _compute_amendment_cost(self):
        """Compute amendment_cost value"""
        for rec in self:
            rec.amendment_cost = sum(
                rec.line_ids.filtered(
                    lambda r: r.display_type == False and r.amendment
                ).mapped("cost")
            )

    @api.depends("line_ids.price", "line_ids.amendment")
    def _compute_amendment_revenue(self):
        """Compute amendment_revenue value"""
        for rec in self:
            rec.amendment_revenue = sum(
                rec.line_ids.filtered(
                    lambda r: r.display_type == False and r.amendment
                ).mapped("price")
            )

    @api.depends("amendment_revenue", "amendment_cost")
    def _compute_amendment_margin(self):
        """Compute amendment_margin value"""
        for rec in self:
            amendment_margin = rec.amendment_revenue - rec.amendment_cost
            rec.amendment_margin = amendment_margin
            rec.amendment_margin_percentage = (
                rec.amendment_revenue and amendment_margin / rec.amendment_revenue or 0
            )

    @api.depends("line_ids.cost")
    def _compute_contracted_cost(self):
        """Compute contracted_cost value"""
        for rec in self:
            rec.contracted_cost = sum(
                rec.line_ids.filtered(lambda r: r.display_type == False).mapped("cost")
            )

    @api.depends("line_ids.price")
    def _compute_contracted_revenue(self):
        """Compute contracted_revenue value"""
        for rec in self:
            rec.contracted_revenue = sum(
                rec.line_ids.filtered(lambda r: r.display_type == False).mapped("price")
            )

    @api.depends("contracted_revenue", "contracted_cost")
    def _compute_contracted_margin(self):
        """Compute contracted_margin value"""
        for rec in self:
            contracted_margin = rec.contracted_revenue - rec.contracted_cost
            rec.contracted_margin = contracted_margin
            rec.contracted_margin_percentage = (
                rec.contracted_revenue
                and contracted_margin / rec.contracted_revenue
                or 0
            )

    @api.depends("actual_revenue", "actual_cost")
    def _compute_actual_margin(self):
        """Compute actual_margin value"""
        for rec in self:
            actual_margin = rec.actual_revenue - rec.actual_cost
            rec.actual_margin = actual_margin
            rec.actual_margin_percentage = (
                rec.actual_revenue and actual_margin / rec.actual_revenue or 0
            )

    def action_draft(self):
        """Action Draft"""
        for rec in self:
            rec.state = "draft"
            # stage = self.env['proposal.stage'].sudo().search([('is_draft', '=', True)], limit=1)
            # if stage.id:
            #     rec.stage_id = stage.id
    
    def action_cancel(self):
        for rec in self:
            rec.state = "cancelled"
            
    def action_send_to_purchase(self):
        """Action Send To Purchase"""
        for rec in self:
            if rec.line_ids.filtered(
                lambda r: r.display_type == False and r.product_uom_qty <= 0
            ):
                raise ValidationError(_("All lines must have Quantity"))
            rec.state = "sent_to_purchase"
            # stage = self.env['proposal.stage'].sudo().search([('is_send_to_purchase', '=', True)], limit=1)
            # if stage.id:
            #     rec.stage_id = stage.id
            rec.execute_activity_plan()

    def action_send_to_sales(self):
        """Action Send To sales"""
        for rec in self:
            if rec.line_ids.filtered(
                lambda r: r.display_type == False and r.unit_cost <= 0
            ):
                raise ValidationError(_("All lines must have Cost"))
            rec.state = "sent_to_sales"
            # stage = self.env['proposal.stage'].sudo().search([('is_send_to_sales', '=', True)], limit=1)
            # if stage.id:
            #     rec.stage_id = stage.id
            rec.execute_activity_plan()

    def action_won(self):
        """Action Won"""
        for rec in self:
            rec.contract_date = fields.Date.today()
            rec.state = "done"
            # stage = self.env['proposal.stage'].sudo().search([('is_done', '=', True)], limit=1)
            # if stage.id:
            #     rec.stage_id = stage.id

    def action_lost_reason(self):
        """Action lost"""
        self.with_context(tracking_disable=True).lost_reason = ""
        return {
            "type": "ir.actions.act_window",
            "res_model": "proposal.proposal",
            "name": _("Lost Reason"),
            "view_mode": "form",
            "target": "new",
            "res_id": self.id,
            "views": [(self.env.ref("proposal.proposal_lost_reason_form").id, "form")],
        }

    def action_update_qty(self):
        """Action Update QTY"""
        return {
            "type": "ir.actions.act_window",
            "res_model": "proposal.proposal",
            "name": _("Update QTY"),
            "view_mode": "form",
            "target": "new",
            "res_id": self.id,
            "views": [(self.env.ref("proposal.proposal_update_qty_form").id, "form")],
        }

    def action_proposal_amendment(self):
        """Action Proposal Amendment"""
        return {
            "type": "ir.actions.act_window",
            "res_model": "proposal.proposal",
            "name": _("Proposal Amendment"),
            "view_mode": "form",
            "target": "new",
            "res_id": self.id,
            "views": [(self.env.ref("proposal.proposal_amendment_form").id, "form")],
        }

    def update_qty(self):
        """Action lost"""
        for rec in self:
            self.action_send_to_purchase()
            rec.activity_schedule(
                activity_type_id=self.env.ref("mail.mail_activity_data_todo").id,
                summary="there are some updates in qty please review them",
                user_id=rec.purchase_responsible_id.id,
            )
            self.attach_snapshot()

    def attach_snapshot(self):
        for rec in self:
            report = self.env["ir.actions.report"]._render_qweb_pdf(
                "proposal.proposal_template", res_ids=self.ids
            )
            self.do_version()
            self.env["ir.attachment"].create(
                {
                    "name": f"{rec.current_version}.pdf",
                    "type": "binary",
                    "datas": base64.b64encode(report[0]),
                    "res_model": self._name,
                    "res_id": rec.id,
                    "mimetype": "application/pdf",
                }
            )

    def action_lost(self):
        """Action lost"""
        for rec in self:
            rec.state = "lost"

    def action_view_purchases(self):
        """:return Purchase action"""
        return {
            "type": "ir.actions.act_window",
            "res_model": "purchase.order",
            "name": _("Purchase Orders"),
            "view_mode": "list,form",
            "domain": [("proposal_id", "=", self.id)],
        }

    def action_view_sales(self):
        """:return sales action"""
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "name": _("Sale Orders"),
            "view_mode": "form",
            "res_id": self.sale_id.id,
        }

    def action_create_so(self):
        """Action Create So"""
        for rec in self:
            rec.sale_id = self.env["sale.order"].create(
                {
                    "partner_id": rec.partner_id.id,
                    "date_order": rec.date_order,
                    "proposal_id": rec.id,
                    "analytic_account_id": rec.analytic_account_id.id,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "product_id": line.product_id.id,
                                "name": line.name,
                                "product_uom_qty": line.product_uom_qty,
                                "product_uom": line.uom_id.id,
                                "analytic_distribution": {
                                    rec.analytic_account_id.id: 100
                                },
                                "tax_id": line.sales_tax_ids.ids,
                                "price_unit": line.unit_price,
                                "display_type": line.display_type,
                                "proposal_line_id": line.id,
                            },
                        )
                        for line in rec.line_ids
                    ],
                }
            )

    def action_apply_amendment(self):
        """Action Apply Amendment"""
        for rec in self:
            rec.sale_id.write(
                {
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "product_id": line.product_id.id,
                                "name": line.name,
                                "product_uom_qty": line.product_uom_qty,
                                "product_uom": line.uom_id.id,
                                "analytic_distribution": {
                                    rec.analytic_account_id.id: 100
                                },
                                "tax_id": line.sales_tax_ids.ids,
                                "price_unit": line.unit_price,
                                "display_type": line.display_type,
                                "proposal_line_id": line.id,
                            },
                        )
                        for line in rec.line_ids.filtered(
                            lambda r: not r.sale_order_line_ids and r.amendment
                        )
                    ]
                }
            )

    def execute_activity_plan(self):
        """Execute Activity Plan"""
        for rec in self:
            activities = (
                self.env["proposal.activity.plan"]
                .sudo()
                .search([("proposal_state", "=", rec.state)])
            )
            for activity in activities:
                for user in activity.user_ids:
                    rec.activity_schedule(
                        activity_type_id=activity.activity_type_id.id,
                        summary=activity.description,
                        user_id=user.id,
                        date_deadline=rec.date_order
                        + relativedelta(days=activity.planned_after or 0),
                    )

    @api.model
    def create(self, vals_list):
        """
        Override create method
         - sequence name
        """
        res = super().create(vals_list)
        res.company_id._create_proposal_sequence()
        if res.name == _("New"):
            res.name = res.company_id.proposal_sequence_id._next()
        res._create_sequence()
        res._create_claim_sequence()
        res.execute_activity_plan()
        return res

    def unlink(self):
        """Override unlink"""
        self.sequence_id.unlink()
        return super().unlink()

    def _group_expand_stage_id(self, stages, domain, order):
        """Expand kanban columnes for stage_id"""
        return self.env["proposal.stage"].search([])


class ProposalLine(models.Model):
    """
    Initialize Proposal Line:
     -
    """

    _name = "proposal.line"
    _description = "Proposal Line"
    _check_company_auto = True
    _inherit = "analytic.mixin"

    name = fields.Char(required=True, string="Description")
    product_id = fields.Many2one(
        "product.product",
    )
    uom_id = fields.Many2one(
        "uom.uom",
        string="Unit Of Measure",
        related="product_id.uom_id",
    )
    product_uom_qty = fields.Float(string="Quantity")
    unit_price = fields.Float(compute="_compute_unit_price", store=True, digits=(16, 5))
    price = fields.Monetary(compute="_compute_price", store=True)
    sales_taxes = fields.Monetary(
        string="Sales Taxes",
        compute="_compute_totals",
        store=True,
        currency_field="currency_id",
    )
    price_after_taxes = fields.Monetary(
        compute="_compute_totals",
        store=True,
        currency_field="currency_id",
    )
    unit_cost = fields.Float(digits=(16, 5))
    cost = fields.Monetary(
        compute="_compute_cost",
        store=True,
    )
    purchase_taxes = fields.Monetary(
        string="Purchase Taxes",
        compute="_compute_totals",
        store=True,
        currency_field="currency_id",
    )
    cost_after_taxes = fields.Monetary(
        compute="_compute_totals",
        store=True,
        currency_field="currency_id",
    )
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id
    )
    proposal_id = fields.Many2one("proposal.proposal", ondelete="cascade")
    proposal_state = fields.Selection(related="proposal_id.state", store=True)
    margin_percentage = fields.Float()
    margin_amount = fields.Float(
        compute="_compute_margin_amount", inverse="_inverse_margin_amount", store=True
    )
    sales_tax_ids = fields.Many2many(
        "account.tax",
        "proposal_sales_tax_rel",
        string="Sales Taxes",
        domain="[('type_tax_use', '=', 'sale')]",
    )
    purchase_tax_ids = fields.Many2many(
        "account.tax",
        "proposal_purchase_tax_rel",
        string="Purchase Taxes",
        domain="[('type_tax_use', '=', 'purchase')]",
    )
    claim_line_ids = fields.One2many("proposal.claim.line", "proposal_line_id")
    vendor_claim_line_ids = fields.One2many(
        "proposal.vendor.claim.line", "proposal_line_id"
    )
    total_claimed_qty = fields.Float(compute="_compute_total_claimed", store=True)
    total_claimed_amount = fields.Float(compute="_compute_total_claimed", store=True)
    display_type = fields.Selection(
        selection=[
            ("line_section", "Section"),
            ("line_note", "Note"),
        ],
        default=False,
    )
    sequence = fields.Integer(string="Sequence", default=10)
    amendment = fields.Boolean()
    sale_order_line_ids = fields.One2many("sale.order.line", "proposal_line_id")

    def _compute_taxes(self, tax_ids, qty, price):
        if tax_ids:
            taxes_res = tax_ids.compute_all(
                price,
                quantity=qty,
                currency=self.currency_id,
                product=self.product_id,
                partner=self.proposal_id.partner_id,
            )
            return sum(map(lambda r: r["amount"], taxes_res["taxes"]))
        return 0

    @api.depends(
        "product_uom_qty",
        "unit_price",
        "unit_cost",
        "sales_tax_ids",
        "purchase_tax_ids",
        "currency_id",
        "cost",
        "price",
    )
    def _compute_totals(self):
        for line in self:
            sales_taxes = line._compute_taxes(
                line.sales_tax_ids,
                line.product_uom_qty,
                line.unit_price,
            )
            purchase_taxes = line._compute_taxes(
                line.purchase_tax_ids,
                line.product_uom_qty,
                line.unit_cost,
            )
            line.purchase_taxes = purchase_taxes
            line.sales_taxes = sales_taxes
            line.cost_after_taxes = line.cost + purchase_taxes
            line.price_after_taxes = line.price + sales_taxes

    @api.depends(
        "claim_line_ids",
        "claim_line_ids.claim_id.state",
        "claim_line_ids.current_qty",
        "claim_line_ids.current_amount",
    )
    def _compute_total_claimed(self):
        """Compute total_claimed value"""
        for rec in self:
            claim_lines = rec.claim_line_ids.filtered(
                lambda r: r.claim_id.state == "done"
            )
            rec.total_claimed_qty = sum(claim_lines.mapped("current_qty"))
            rec.total_claimed_amount = sum(claim_lines.mapped("current_amount"))

    @api.depends("unit_cost", "margin_percentage")
    def _compute_margin_amount(self):
        """Compute margin_amount value"""
        for rec in self:
            rec.margin_amount = (
                rec.unit_cost / (1 - rec.margin_percentage)
            ) - rec.unit_cost

    @api.onchange("unit_cost", "margin_amount")
    def _inverse_margin_amount(self):
        """Compute margin_amount value"""
        for rec in self:
            rec.margin_percentage = (
                (-rec.unit_cost - rec.margin_amount)
                and -rec.margin_amount / (-rec.unit_cost - rec.margin_amount)
                or 0
            )

    @api.depends("margin_amount", "unit_cost")
    def _compute_unit_price(self):
        """Compute unit_price value"""
        for rec in self:
            rec.unit_price = rec.unit_cost + rec.margin_amount

    @api.depends("unit_price", "product_uom_qty")
    def _compute_price(self):
        """Compute price value"""
        for rec in self:
            rec.price = rec.unit_price * rec.product_uom_qty

    @api.depends("unit_cost", "product_uom_qty")
    def _compute_cost(self):
        """Compute cost value"""
        for rec in self:
            rec.cost = rec.unit_cost * rec.product_uom_qty

    @api.onchange("product_id")
    def _onchange_product_id(self):
        """product_id"""
        self.name = self.product_id.name
        self.uom_id = self.product_id.uom_id.id
