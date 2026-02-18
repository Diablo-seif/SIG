import jwt
import datetime
import secrets
import base64
from odoo import http, fields
from odoo.http import request
from datetime import datetime, timedelta


SECRET_KEY = "SECRET_KEY"


class CentralSystemIntegrationControllerController(http.Controller):

    def _generate_jwt_token(self, company):
        """Generate a JWT access token with expiration."""
        payload = {
            "company_id": company.id,
            "exp": datetime.utcnow() + timedelta(hours=24),  # Expires in 24 hours
            "iat": datetime.utcnow(),  # Issued at
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    def _decode_jwt_token(self, token):
        """Decode JWT and return user if valid."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            company = request.env["res.company"].sudo().browse(payload["company_id"])
            return company if company.exists() else None
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def _generate_refresh_token(self, user):
        """Generate a long-lived refresh token."""
        return secrets.token_hex(32)

    def _build_domain_filters(self, params, domain):
        # --- Build domain filters ---
        # domain =

        # Creation date range
        date_from = params.get("create_date_from")
        date_to = params.get("create_date_to")
        if date_from:
            domain.append(("create_date", ">=", date_from))
        if date_to:
            domain.append(("create_date", "<=", date_to))

        # Update date range
        update_from = params.get("write_date_from")
        update_to = params.get("write_date_to")
        if update_from:
            domain.append(("write_date", ">=", update_from))
        if update_to:
            domain.append(("write_date", "<=", update_to))

        # Created by specific user
        if params.get("created_by"):
            domain.append(("create_uid", "=", int(params["created_by"])))
        return domain

    def _prepare_data(self, params, model_name, domain):
        page = int(params.get("page", 1))
        page_size = int(params.get("page_size", 10))
        offset = (page - 1) * page_size

        domain = self._build_domain_filters(params, domain)

        # Limit number of items
        limit = int(params.get("limit", page_size))

        # --- Order by field ---
        order_by = params.get("order_by", "create_date")
        order_type = params.get("order_type", "desc")  # 'asc' or 'desc'

        if limit == 1 and page == 98:  # Prevent error from Odoo ORM
            order_type = "desc"

        order = f"{order_by} {order_type}"

        # --- Query records ---
        model = request.env[model_name].sudo()
        total_count = model.search_count(domain)
        total_pages = (total_count + page_size - 1) // page_size

        records = model.search(domain, offset=offset, limit=limit, order=order)
        # all_records = model.search(domain, order=order)
        # records = all_records[offset : offset + limit]

        return {
            "success": True,
            "records": records,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
            },
        }

    @http.route(
        "/central_system_integration/login",
        type="json",
        auth="public",
        methods=["POST"],
    )
    def login(self, **params):
        """Authenticate user and return access & refresh tokens."""
        company = (
            request.env["res.company"]
            .sudo()
            .search(
                [
                    ("integration_token", "=", params.get("integration_token")),
                ],
                limit=1,
            )
        )
        if company:
            access_token = self._generate_jwt_token(company)
            refresh_token = self._generate_refresh_token(company)
            company.sudo().write({"refresh_token": refresh_token})
            return {
                "success": True,
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        return {"success": False, "error": "Invalid credentials"}

    @http.route(
        "/central_system_integration/get_users",
        type="json",
        auth="public",
        methods=["POST"],
    )
    def central_system_integration_get_users(self, **params):
        """Fetch users only if the token is valid."""
        access = self._decode_jwt_token(params.get("access_token"))
        if not access:
            return {"success": False, "error": "Invalid or expired token"}
        try:
            data = self._prepare_data(params, "res.users", [])
            users = data["records"]

            return {
                "success": True,
                "users": [
                    {
                        "id": user.id,
                        "created_by": user.create_uid.id,
                        "create_date": user.create_date,
                        "last_updated_by": (user.write_uid.id),
                        "last_update_date": user.write_date,
                        "name": user.name,
                        "email": user.login,
                        "phone": user.partner_id.phone,
                    }
                    for user in users
                ],
                "pagination": data["pagination"],
            }
        except Exception as e:
            return {"success": False, "error": e}

    @http.route(
        "/central_system_integration/get_partners",
        type="json",
        auth="public",
        methods=["POST"],
    )
    def central_system_integration_get_partners(self, **params):
        """Fetch partners only if the token is valid."""
        access = self._decode_jwt_token(params.get("access_token"))
        if not access:
            return {"success": False, "error": "Invalid or expired token"}
        try:
            # moves = request.env["account.move"].sudo().search([])
            # partner_ids = moves.mapped("partner_id")
            # model = request.env['res.partner'].sudo().browse(partner_ids)
            domain = ["|", ("customer_rank", ">", 0), ("supplier_rank", ">", 0)]
            data = self._prepare_data(params, "res.partner", domain)
            partners = data["records"]

            return {
                "success": True,
                "partners": [
                    {
                        "id": partner.id,
                        "created_by": partner.create_uid.name,
                        "create_date": partner.create_date,
                        "updated_by": partner.write_uid.name,
                        "write_date": partner.write_date,
                        "code": partner.ref,
                        "type": partner.company_type,
                        "name": partner.name,
                        "is_customer": partner.customer_rank > 0,
                        "is_supplier": partner.supplier_rank > 0,
                        "address": partner.street,
                        "city": partner.city,
                        "country": partner.country_id.name,
                        "vat_number": partner.vat,
                        "commercial_register": partner.commercial_register,
                        "national_id": partner.national_id,
                        "passport": partner.passport,
                    }
                    for partner in partners
                ],
                "pagination": data["pagination"],
            }
        except Exception as e:
            return {"success": False, "error": e}

    @http.route(
        "/central_system_integration/get_invoices",
        type="json",
        auth="public",
        methods=["POST"],
    )
    def central_system_integration_get_all_get_invoices(self, **params):
        access = self._decode_jwt_token(params.get("access_token"))
        if not access:
            return {"success": False, "error": "Invalid or expired token"}
        try:
            # moves = request.env["account.move"].sudo().search([])
            domain = [("move_type", "=", "out_invoice")]
            data = self._prepare_data(params, "account.move", domain)
            records = data["records"]

            MOVE_TYPE_MAPPING = {
                "out_invoice": "customer_invoice",
                "out_refund": "customer_refund",
                "in_invoice": "vendor_invoice",
                "in_refund": "vendor_refund",
            }
            PAYMENT_STATE_MAPPING = {
                "not_paid": "Not Paid",
                "paid": "Paid",
                "partial": "Partial Payment",
            }
            invoices = []
            for invoice in records:
                lines = []
                for line in invoice.invoice_line_ids:
                    lines.append(
                        {
                            "item_code": line.product_id.default_code or "",
                            "item_from_dropdown": line.product_id.name or "",
                            "item_price": line.price_subtotal,
                            "item_price_local": invoice.currency_id._convert(
                                line.price_subtotal,
                                invoice.company_id.currency_id,
                                invoice.company_id,
                                invoice.create_date,
                            ),
                            "discount": line.price_unit
                            * line.quantity
                            * (line.discount / 100.0),
                            "tax": [tax.id for tax in line.tax_ids],
                        }
                    )
                    exchange_rate = invoice.amount_total / invoice.currency_id._convert(
                        invoice.amount_total,
                        invoice.company_id.currency_id,
                        invoice.company_id,
                        invoice.create_date,
                    )
                invoices.append(
                    {
                        "id": invoice.id,
                        "created_by": invoice.create_uid.id,
                        "create_date": str(invoice.create_date),
                        "last_updated_by": invoice.write_uid.id,
                        "write_date": str(invoice.write_date),
                        "invoice_number": invoice.name,
                        "invoice_type": MOVE_TYPE_MAPPING[invoice.move_type],
                        "customer_or_vendor": invoice.partner_id.id,
                        "invoice_date": str(invoice.invoice_date),
                        "due_date": str(invoice.invoice_date_due),
                        "currency": invoice.currency_id.name,
                        "exchange_rate": exchange_rate,
                        "lines": lines,
                        "discount": sum(
                            line.price_unit * line.quantity * (line.discount / 100.0)
                            for line in invoice.invoice_line_ids
                        ),
                        "amount_tax": invoice.amount_tax,
                        "amount_untaxed": invoice.amount_untaxed,
                        "amount_total": invoice.amount_total,
                        "sales_person": invoice.invoice_user_id.id,
                        "customer_name": invoice.partner_id.id,
                        "paid_amount": invoice.amount_total - invoice.amount_residual,
                        "remaining_amount": invoice.amount_residual,
                        "invoice_status": PAYMENT_STATE_MAPPING[invoice.payment_state],
                        "e_invoice_number": False,
                        "description": invoice.payment_reference,
                    }
                )
            return {
                "success": True,
                "invoices": invoices,
                "pagination": data["pagination"],
            }
        except Exception as e:
            return {"success": False, "error": e}

    @http.route(
        "/central_system_integration/get_payments",
        type="json",
        auth="public",
        methods=["POST"],
    )
    def central_system_integration_get_payments(self, **params):
        access = self._decode_jwt_token(params.get("access_token"))
        if not access:
            return {"success": False, "error": "Invalid or expired token"}
        try:
            domain = []
            data = self._prepare_data(params, "account.payment", domain)
            records = data["records"]
            payments = []
            for payment in records:
                exchange_rate = 1.0
                if payment.currency_id != payment.company_id.currency_id:
                    exchange_rate = payment.amount / payment.currency_id._convert(
                        payment.amount,
                        payment.company_id.currency_id,
                        payment.company_id,
                        payment.date,
                    )
                payments.append(
                    {
                        "id": payment.id,
                        "created_by": payment.create_uid.id,
                        "create_date": str(payment.create_date),
                        "last_updated_by": payment.write_uid.id,
                        "write_date": str(payment.write_date),
                        "transaction_number": payment.name,
                        "transaction_date": str(payment.date),
                        "customer_or_vendor": payment.partner_id.id,
                        "amount": payment.amount,
                        "currency_code": payment.currency_id.name,
                        "exchange_rate": exchange_rate,
                        "payment_method": payment.payment_method_id.code,
                        "check_number": (
                            payment.check_number
                            if payment.payment_method_id.code == "check"
                            else ""
                        ),
                        "bank": (
                            payment.journal_id.name
                            if payment.payment_method_id.code == "bank"
                            else ""
                        ),
                        "payment_status": payment.payment_type,
                        "transaction_description": payment.ref or "",
                    }
                )

            return {
                "success": True,
                "payments": payments,
                "pagination": data["pagination"],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @http.route(
        "/central_system_integration/get_journal_entries",
        type="json",
        auth="public",
        methods=["POST"],
    )
    def central_system_integration_get_journal_entries(self, **params):
        access = self._decode_jwt_token(params.get("access_token"))
        if not access:
            return {"success": False, "error": "Invalid or expired token"}
        try:
            domain = [("move_type", "=", "entry")]
            data = self._prepare_data(params, "account.move", domain)
            records = data["records"]

            journal_entries = []
            for entry in records:
                move_lines = []
                for line in entry.line_ids:
                    analytic_account = False
                    analytic_distribution = line.analytic_distribution or {}
                    if analytic_distribution:
                        account_id = next(iter(analytic_distribution.keys()), False)
                        if account_id:
                            analytic_account = (
                                request.env["account.analytic.account"]
                                .sudo()
                                .browse(int(account_id))
                            )

                    move_lines.append(
                        {
                            "id": line.id,
                            "created_by": line.create_uid.id,
                            "create_date": str(line.create_date),
                            "last_updated_by": line.write_uid.id,
                            "write_date": str(line.write_date),
                            "parent_entry_id": entry.id,
                            "account": line.account_id.id,
                            "debit_amount": line.debit,
                            "credit_amount": line.credit,
                            "description": line.name or "",
                            "project": (
                                analytic_account.name if analytic_account else ""
                            ),
                            "foreign_amount": (
                                line.amount_currency if line.currency_id else 0.0
                            ),
                            "currency": (
                                line.currency_id.name if line.currency_id else ""
                            ),
                        }
                    )

                journal_entries.append(
                    {
                        "id": entry.id,
                        "created_by": entry.create_uid.id,
                        "create_date": str(entry.create_date),
                        "last_updated_by": entry.write_uid.id,
                        "write_date": str(entry.write_date),
                        "entry_number": entry.name,
                        "entry_date": str(entry.date),
                        "description": entry.ref or "",
                        "state": entry.state,
                        "move_lines": move_lines,
                    }
                )

            return {
                "success": True,
                "journal_entries": journal_entries,
                "pagination": data["pagination"],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @http.route(
        "/central_system_integration/get_exchange_rates",
        type="json",
        auth="public",
        methods=["POST"],
    )
    def central_system_integration_get_exchange_rates(self, **params):
        access = self._decode_jwt_token(params.get("access_token"))
        if not access:
            return {"success": False, "error": "Invalid or expired token"}
        try:
            # Search for res.currency.rate records
            domain = []
            data = self._prepare_data(params, "res.currency.rate", domain)
            records = data["records"]

            exchange_rates = []
            for rate in records:
                exchange_rates.append(
                    {
                        "id": rate.id,
                        "created_by": rate.create_uid.id,
                        "create_date": str(rate.create_date),
                        "last_updated_by": rate.write_uid.id,
                        "write_date": str(rate.write_date),
                        "date": str(rate.name),
                        "currency_code": rate.currency_id.name,
                        # "currency_id": rate.currency_id.id,
                        "currency_name": rate.currency_id.full_name
                        or rate.currency_id.name,
                        "exchange_rate": 1 / rate.rate if rate.rate else 0,
                        # "company_currency": rate.company_id.currency_id.name,
                        # "company_currency_id": rate.company_id.currency_id.id,
                        # "inverse_rate": 1 / rate.rate if rate.rate else 0,
                    }
                )

            return {
                "success": True,
                "exchange_rates": exchange_rates,
                "pagination": data["pagination"],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @http.route(
        "/central_system_integration/get_chart_of_accounts",
        type="json",
        auth="public",
        methods=["POST"],
    )
    def central_system_integration_get_chart_of_accounts(self, **params):
        access = self._decode_jwt_token(params.get("access_token"))
        if not access:
            return {"success": False, "error": "Invalid or expired token"}

        try:
            domain = []
            data = self._prepare_data(params, "account.account", domain)
            records = data["records"]

            accounts = []
            seen_codes = set()

            for account in records:
                if account.code in seen_codes:
                    continue

                seen_codes.add(account.code)

                accounts.append(
                    {
                        "id": account.id,
                        "created_by": account.create_uid.id,
                        "create_date": str(account.create_date),
                        "last_updated_by": account.write_uid.id,
                        "write_date": str(account.write_date),
                        "name": account.name,
                        "code": account.code,
                        "account_type": account.account_type,
                        "currency": "EGP",
                        "company_id": account.company_id.id,
                        "deprecated": account.deprecated,
                        "reconcile": account.reconcile,
                    }
                )

            return {
                "success": True,
                "accounts": accounts,
                "pagination": data["pagination"],
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    @http.route(
        "/central_system_integration/get_banks",
        type="json",
        auth="public",
        methods=["POST"],
    )
    def central_system_integration_get_banks(self, **params):
        access = self._decode_jwt_token(params.get("access_token"))
        if not access:
            return {"success": False, "error": "Invalid or expired token"}
        try:
            domain = []
            data = self._prepare_data(params, "res.bank", domain)
            records = data["records"]

            banks = []
            for bank in records:
                banks.append(
                    {
                        "id": bank.id,
                        "created_by": bank.create_uid.id,
                        "create_date": str(bank.create_date),
                        "last_updated_by": bank.write_uid.id,
                        "write_date": str(bank.write_date),
                        "name": bank.name,
                        "bic": bank.bic or "",
                    }
                )

            return {
                "success": True,
                "banks": banks,
                "pagination": data["pagination"],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @http.route(
        "/central_system_integration/get_bank_accounts",
        type="json",
        auth="public",
        methods=["POST"],
    )
    def central_system_integration_get_bank_accounts(self, **params):
        access = self._decode_jwt_token(params.get("access_token"))
        if not access:
            return {"success": False, "error": "Invalid or expired token"}
        try:
            domain = [("type", "=", "bank")]
            data = self._prepare_data(params, "account.journal", domain)
            records = data["records"]

            accounts = []
            for account in records:
                accounts.append(
                    {
                        "id": account.id,
                        "created_by": account.create_uid.id,
                        "create_date": str(account.create_date),
                        "last_updated_by": account.write_uid.id,
                        "write_date": str(account.write_date),
                        "bank_name": account.bank_id.name if account.bank_id else "",
                        "bank_id": account.bank_id.id if account.bank_id else False,
                        "account_number": account.bank_account_id.acc_number or "",
                        "currency": (
                            account.currency_id.name if account.currency_id else ""
                        ),
                        "currency_id": (
                            account.currency_id.id if account.currency_id else False
                        ),
                        "account": (
                            account.default_account_id.name
                            if account.default_account_id
                            else False
                        ),
                        "account_id": (
                            account.default_account_id.id
                            if account.default_account_id
                            else False
                        ),
                    }
                )
            return {
                "success": True,
                "bank_accounts": accounts,
                "pagination": data["pagination"],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @http.route(
        "/central_system_integration/get_treasury_accounts",
        type="json",
        auth="public",
        methods=["POST"],
    )
    def central_system_integration_get_treasury_accounts(self, **params):
        access = self._decode_jwt_token(params.get("access_token"))
        if not access:
            return {"success": False, "error": "Invalid or expired token"}
        try:
            domain = [("type", "=", "cash")]
            data = self._prepare_data(params, "account.journal", domain)
            records = data["records"]

            treasury_accounts = []
            for account in records:
                treasury_accounts.append(
                    {
                        "id": account.id,
                        "created_by": account.create_uid.id,
                        "create_date": str(account.create_date),
                        "last_updated_by": account.write_uid.id,
                        "write_date": str(account.write_date),
                        "name": account.name,
                        "account": (
                            account.default_account_id.name
                            if account.default_account_id
                            else False
                        ),
                        "account_id": (
                            account.default_account_id.id
                            if account.default_account_id
                            else False
                        ),
                        "currency": (
                            account.currency_id.name if account.currency_id else ""
                        ),
                        "currency_id": (
                            account.currency_id.id if account.currency_id else False
                        ),
                    }
                )

            return {
                "success": True,
                "treasury_accounts": treasury_accounts,
                "pagination": data["pagination"],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @http.route(
        "/central_system_integration/get_projects",
        type="json",
        auth="public",
        methods=["POST"],
    )
    def central_system_integration_get_projects(self, **params):
        access = self._decode_jwt_token(params.get("access_token"))
        if not access:
            return {"success": False, "error": "Invalid or expired token"}
        try:
            # Search for project records
            domain = [("proposal_id.contracted_revenue", ">", 0)]
            data = self._prepare_data(params, "project.project", domain)
            records = data["records"]

            # Mapping dictionaries
            PROJECT_TYPE_MAPPING = {
                "construction": "بناء",
                "it": "تكنولوجيا المعلومات",
                "consulting": "استشارات",
                "other": "أخرى",
            }

            PROJECT_STATUS_MAPPING = {
                "draft": "لم يبدأ",
                "in_progress": "قيد التنفيذ",
                "pending": "معلق",
                "done": "منتهي",
                "cancel": "ملغى",
            }

            PROJECT_TIMEFRAME_MAPPING = {
                "short": "قصير الأجل (أقل من عام)",
                "long": "طويل الأجل (أكثر من عام)",
            }

            projects = []
            for project in records:
                # Calculate financials
                total_costs = (
                    sum(
                        analytic_line.amount
                        for analytic_line in request.env["account.analytic.line"]
                        .sudo()
                        .search([("project_id", "=", project.id), ("amount", "<", 0)])
                    )
                    * -1
                )

                total_income = sum(
                    analytic_line.amount
                    for analytic_line in request.env["account.analytic.line"]
                    .sudo()
                    .search([("project_id", "=", project.id), ("amount", ">", 0)])
                )
                contract_duration = ""
                # if project.date_start and project.date_end:
                #     days = (project.date_end - project.date_start).days
                #     contract_duration = f"{days} days" if days > 0 else ""
                # if project.proposal_id.contracted_revenue > 0:
                projects.append(
                    {
                        "id": project.id,
                        "created_by": project.create_uid.id,
                        "create_date": str(project.create_date),
                        "last_updated_by": project.write_uid.id,
                        "write_date": str(project.write_date),
                        "project_code": project.code or "",
                        "project_name": project.name,
                        # "project_type": PROJECT_TYPE_MAPPING.get(
                        #     project.project_type or "other", "أخرى"
                        # ),
                        # "project_type_code": project.project_type or "",
                        "location": project.location or "",
                        "project_type": project.project_type or "",
                        "contracting_party": project.contracting_party or "",
                        "contractor": project.contractor or "",
                        "expected_number_of_hours": project.expected_number_of_hours
                        or "",
                        "number_of_hours_consumed": project.number_of_hours_consumed
                        or "",
                        "description": project.description or "",
                        "timeframe": PROJECT_TIMEFRAME_MAPPING.get(
                            (
                                "long"
                                if project.date
                                and (project.date - project.date_start).days > 365
                                else "short"
                            ),
                            "قصير الأجل",
                        ),
                        "status": PROJECT_STATUS_MAPPING.get(
                            project.stage_id.name, "لم يبدأ"
                        ),
                        # "status_code": project.stage_id.name,
                        "completion_percentage": project.progress or 0,
                        "planned_start_date": (
                            str(project.date_start) if project.date_start else ""
                        ),
                        "planned_end_date": (str(project.date) if project.date else ""),
                        "actual_start_date": (
                            str(project.actual_start_date)
                            if project.actual_start_date
                            else ""
                        ),
                        "actual_end_date": (
                            str(project.actual_end_date)
                            if project.actual_end_date
                            else ""
                        ),
                        "project_manager": (
                            project.user_id.id if project.user_id else None
                        ),
                        "client": (
                            project.partner_id.id if project.partner_id else None
                        ),
                        "contract_value": project.proposal_id.contracted_revenue or 0,
                        "contract_currency": (
                            project.proposal_id.currency_id.name
                            if project.proposal_id.currency_id
                            else ""
                        ),
                        "contract_currency_id": project.proposal_id.currency_id.id,
                        # "contract_exchange_rate": project.contract_exchange_rate or 1.0,
                        "contract_date": (
                            str(project.proposal_id.contract_date)
                            if project.proposal_id.contract_date
                            else ""
                        ),
                        "contract_duration": contract_duration,
                        # "contractors": [
                        #     {"id": partner.id, "name": partner.name}
                        #     for partner in project.contractor_ids
                        # ],
                        "total_costs": total_costs,
                        "total_income": total_income,
                        "total_expenses": total_costs,  # Same as total_costs
                        "total_payments": total_income,  # Same as total_income
                        "total_due": (
                            project.proposal_id.contracted_revenue - total_income
                            if project.proposal_id.contracted_revenue
                            else 0
                        ),
                        # "team_members": [
                        #     {"id": member.id, "name": member.name}
                        #     for member in project.member_ids
                        # ],
                    }
                )

            return {
                "success": True,
                "projects": projects,
                "pagination": data["pagination"],
                "status_mapping": PROJECT_STATUS_MAPPING,
                "type_mapping": PROJECT_TYPE_MAPPING,
                "timeframe_mapping": PROJECT_TIMEFRAME_MAPPING,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @http.route(
        "/central_system_integration/get_budget_data",
        type="json",
        auth="public",
        methods=["POST"],
    )
    def central_system_integration_get_budget_data(self, **params):
        access = self._decode_jwt_token(params.get("access_token"))
        if not access:
            return {"success": False, "error": "Invalid or expired token"}

        try:
            # Date range
            date_from_str, date_to_str = self._get_date_range(params)

            date_from = datetime.strptime(str(date_from_str), "%Y-%m-%d").date()
            date_to = datetime.strptime(str(date_to_str), "%Y-%m-%d").date()

            duration = date_to - date_from
            date_to_prev = date_from - timedelta(days=1)
            date_from_prev = date_to_prev - duration

            Account = request.env["account.account"].sudo()
            MoveLine = request.env["account.move.line"].sudo()

            # VALID sub_category keys only
            valid_sub_categories = [
                "fixed_asset_net",
                "intangible_asset_net",
                "project_under_process",
                "financial_investment_in_sister_companies",
                "other_non_current_assets",
                "cash",
                "receivables_and_notes_receivable_account",
                "account_receivable",
                "operations_under_process",
                "paid_up_capital",
                "legal_reserve",
                "retained_earning",
                "current_earning",
                "payables_and_notes_payable",
                "account_payable",
                "non_current_liabilities",
            ]

            # group only valid ones
            sub_categories = Account.read_group(
                [("sub_category", "in", valid_sub_categories)],
                ["sub_category"],
                ["sub_category"],
            )

            results = []

            for group in sub_categories:
                sub_category = group["sub_category"]
                accounts = Account.search([("sub_category", "=", sub_category)])

                main_category = accounts[0].category if accounts else None

                current_lines = MoveLine.search(
                    [
                        ("account_id", "in", accounts.ids),
                        ("date", ">=", date_from),
                        ("date", "<=", date_to),
                        ("parent_state", "=", "posted"),
                    ]
                )

                previous_lines = MoveLine.search(
                    [
                        ("account_id", "in", accounts.ids),
                        ("date", ">=", date_from_prev),
                        ("date", "<=", date_to_prev),
                        ("parent_state", "=", "posted"),
                    ]
                )

                results.append(
                    {
                        "category": main_category,
                        "sub_category": sub_category,
                        "code": sub_category,
                        "amount_current_period": sum(
                            l.debit - l.credit for l in current_lines
                        ),
                        "amount_previous_period": sum(
                            l.debit - l.credit for l in previous_lines
                        ),
                    }
                )

            return {
                "success": True,
                "details": results,
                "date_current_period": {"from": str(date_from), "to": str(date_to)},
                "date_previous_period": {
                    "from": str(date_from_prev),
                    "to": str(date_to_prev),
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    @http.route(
        "/central_system_integration/get_financial_analysis",
        type="json",
        auth="public",
        methods=["POST"],
    )
    def central_system_integration_get_financial_analysis(self, **params):
        access = self._decode_jwt_token(params.get("access_token"))
        if not access:
            return {"success": False, "error": "Invalid or expired token"}

        try:
            # Get date range from params or use defaults
            date_from, date_to = self._get_date_range(params)
            AccountMoveLine = request.env["account.move.line"]

            income_accounts = (
                request.env["account.account"]
                .sudo()
                .search(
                    [
                        (
                            "account_type",
                            "in",
                            ["income", "income_other", "income_regular"],
                        )
                    ]
                )
            )
            expense_accounts = (
                request.env["account.account"]
                .sudo()
                .search(
                    [
                        (
                            "account_type",
                            "in",
                            ["expense", "expense_direct_cost", "expense_depreciation"],
                        )
                    ]
                )
            )
            income = sum(
                line.credit - line.debit
                for line in AccountMoveLine.sudo().search(
                    [
                        ("account_id", "in", income_accounts.ids),
                        ("date", ">=", date_from),
                        ("date", "<=", date_to),
                        ("parent_state", "=", "posted"),
                    ]
                )
            )
            expenses = sum(
                line.debit - line.credit
                for line in AccountMoveLine.sudo().search(
                    [
                        ("account_id", "in", expense_accounts.ids),
                        ("date", ">=", date_from),
                        ("date", "<=", date_to),
                        ("parent_state", "=", "posted"),
                    ]
                )
            )
            profit = income - expenses

            return {
                "success": True,
                "details": [
                    {
                        "إجمالي اإليرادات": "name",
                        "code": "total_income_financial_statement",
                        "amount_current_period": income,
                    },
                    {
                        "إجمالي األرباح": "name",
                        "code": "total_profit_financial_statement",
                        "amount_current_period": profit,
                    },
                    {
                        "إجمالي التبرعات": "name",
                        "code": "total_donation_financial_statement",
                        "amount_current_period": 0,
                    },
                ],
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_date_range(self, params):
        """Get date range from params or use sensible defaults"""
        date_from = params.get("date_from")
        date_to = params.get("date_to")

        if not date_from or not date_to:
            # Default to current fiscal year if no dates provided
            fiscal_year = (
                request.env["account.fiscal.year"]
                .sudo()
                .search(
                    [
                        ("company_id", "=", request.env.company.id),
                        ("date_from", "<=", fields.Date.today()),
                        ("date_to", ">=", fields.Date.today()),
                    ],
                    limit=1,
                )
            )

            if fiscal_year:
                date_from = fiscal_year.date_from
                date_to = fiscal_year.date_to
            else:
                # Fallback to current year if no fiscal year defined
                today = fields.Date.today()
                date_from = today.replace(month=1, day=1)
                date_to = today.replace(month=12, day=31)

        return date_from, date_to

    @http.route(
        "/central_system_integration/get_capital_structure",
        type="json",
        auth="public",
        methods=["POST"],
    )
    def central_system_integration_get_capital_structure(self, **params):
        access = self._decode_jwt_token(params.get("access_token"))
        if not access:
            return {"success": False, "error": "Invalid or expired token"}

        try:
            # Get current company
            company = request.env.company
            capital_account = (
                request.env["account.account"]
                .sudo()
                .search(
                    [
                        ("company_id", "=", company.id),
                        ("code", "=like", "3%"),
                    ],
                    limit=1,
                )
            )
            domain = [("account_id", "=", capital_account.id)]
            data = self._prepare_data(params, "account.move.line", domain)
            records = data["records"]

            return {
                "success": True,
                "name": "تقرير رأس المال",
                "code": "paid_up_capital",
                "details": [
                    {
                        "رأس المال المدفوع": "name",
                        "code": "paid_up_capital",
                        "amount_current_period": sum(records.mapped("credit")),
                    }
                ],
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    @http.route(
        "/central_system_integration/get_balance_sheet",
        type="json",
        auth="public",
        methods=["POST"],
    )
    def central_system_integration_get_balance_sheet(self, **params):
        """
        Returns account move lines grouped by sub_category in a balance sheet format
        Parameters:
        - start_date: Start date in YYYY-MM-DD format
        - end_date: End date in YYYY-MM-DD format
        - period: 'quarterly', 'yearly', or 'monthly'
        """
        # Get current year and previous year dates based on period
        access = self._decode_jwt_token(params.get("access_token"))
        if not access:
            return {"success": False, "error": "Invalid or expired token"}

        try:
            today = datetime.utcnow().date()
            period = params.get("period")
            start_date = params.get("start_date")
            end_date = params.get("end_date")

            if period == "quarterly":
                # For current year quarter
                current_year_start = datetime(
                    today.year, ((today.month - 1) // 3) * 3 + 1, 1
                ).date()
                current_year_end = datetime(
                    today.year, ((today.month - 1) // 3 + 1) * 3, 1
                ).date()

                # For previous year same quarter
                prev_year_start = datetime(
                    today.year - 1, ((today.month - 1) // 3) * 3 + 1, 1
                ).date()
                prev_year_end = datetime(
                    today.year - 1, ((today.month - 1) // 3 + 1) * 3, 1
                ).date()

            # Override with provided dates if available
            if start_date:
                current_year_start = datetime.strptime(start_date, "%Y-%m-%d").date()
            if end_date:
                current_year_end = datetime.strptime(end_date, "%Y-%m-%d").date()
                prev_year_start = datetime(
                    current_year_start.year - 1,
                    current_year_start.month,
                    current_year_start.day,
                ).date()
                prev_year_end = datetime(
                    current_year_end.year - 1,
                    current_year_end.month,
                    current_year_end.day,
                ).date()

            # Get all asset categories
            categories = (
                request.env["account.account"]
                .sudo()
                .search_read([("sub_category", "!=", False)], ["sub_category"])
            )

            unique_categories = list(set([c["sub_category"] for c in categories]))

            result = []

            for category in unique_categories:
                # Current year amounts
                current_year_lines = (
                    request.env["account.move.line"]
                    .sudo()
                    .search(
                        [
                            ("account_id.sub_category", "=", category),
                            ("date", ">=", current_year_start),
                            ("date", "<=", current_year_end),
                        ]
                    )
                )
                current_year_amount = sum(line.balance for line in current_year_lines)

                # Previous year amounts
                prev_year_lines = (
                    request.env["account.move.line"]
                    .sudo()
                    .search(
                        [
                            ("account_id.sub_category", "=", category),
                            ("date", ">=", prev_year_start),
                            ("date", "<=", prev_year_end),
                        ]
                    )
                )
                prev_year_amount = sum(line.balance for line in prev_year_lines)

                result.append(
                    {
                        "category": current_year_lines.mapped("type"),
                        "sub_category": self._get_category_label(category),
                        "period": "ربع سنوي" if period == "quarterly" else "سنوي",
                        "current_year": {
                            "start_date": current_year_start.strftime("%Y/%m/%d"),
                            "end_date": current_year_end.strftime("%Y/%m/%d"),
                            "amount": current_year_amount,
                        },
                        "previous_year": {
                            "start_date": prev_year_start.strftime("%Y/%m/%d"),
                            "end_date": prev_year_end.strftime("%Y/%m/%d"),
                            "amount": prev_year_amount,
                        },
                    }
                )

            return {
                "success": True,
                "result": result,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_category_label(self, category):
        mapping = {
            "fixed_assets": "صافي الأصول الثابتة",
            "intangible_assets": "صافي الأصول غير الملموسة",
            "projects_construction": "المشروعات تحت التنفيذ",
            "financial_investments": "استثمارات مالية في شركات شقيقة",
            "other_assets": "الأصول الأخرى",
            "paid_capital": "رأس المال المدفوع",
            "legal_reserve": "الاحتياطي القانوني",
            "retained_earnings": "الأرباح المرحلة",
            "net_profit": "صافي ربح العام",
            "suppliers_payable": "الموردون وأوراق الدفع",
            "long_term_liabilities": "الإلتزامات طويلة الأجل",
        }
        return mapping.get(category, category)

    @http.route(
        "/central_system_integration/get_profit_and_loss",
        type="json",
        auth="public",
        methods=["POST"],
    )
    def central_system_integration_get_profit_and_loss(self, **params):
        access = self._decode_jwt_token(params.get("access_token"))
        if not access:
            return {"success": False, "error": "Invalid or expired token"}

        try:
            company = request.env.company

            # --- Get current period dates from params ---
            date_from_str = params.get("date_from")
            date_to_str = params.get("date_to")

            if not (date_from_str and date_to_str):
                return {
                    "success": False,
                    "error": "Missing date_from or date_to in params",
                }

            date_from = fields.Date.from_string(date_from_str)
            date_to = fields.Date.from_string(date_to_str)
            period_days = (date_to - date_from).days + 1

            # --- Calculate previous period dates ---
            previous_date_to = date_from - timedelta(days=1)
            previous_date_from = previous_date_to - timedelta(days=period_days - 1)

            # --- Find accounts ---
            revenue_accounts = (
                request.env["account.account"]
                .sudo()
                .search(
                    [
                        ("company_id", "=", company.id),
                        ("code", "=like", "4%"),
                    ]
                )
            )
            cost_accounts = (
                request.env["account.account"]
                .sudo()
                .search(
                    [
                        ("company_id", "=", company.id),
                        ("code", "=like", "5%"),
                    ]
                )
            )

            def get_amount_for_period(accounts, start_date, end_date):
                domain = [
                    ("account_id", "in", accounts.ids),
                    ("date", ">=", start_date),
                    ("date", "<=", end_date),
                ]
                records = request.env["account.move.line"].sudo().search(domain)
                debit = sum(records.mapped("debit"))
                credit = sum(records.mapped("credit"))
                return credit - debit

            # --- Compute both periods ---
            revenue_current = get_amount_for_period(
                revenue_accounts, date_from, date_to
            )
            cost_current = get_amount_for_period(cost_accounts, date_from, date_to)

            revenue_previous = get_amount_for_period(
                revenue_accounts, previous_date_from, previous_date_to
            )
            cost_previous = get_amount_for_period(
                cost_accounts, previous_date_from, previous_date_to
            )

            # --- Return formatted response ---
            return {
                "success": True,
                "name": "تقرير النشاط الجاري",
                "code": "current_operation",
                "details": [
                    {
                        "name": "إيرادات النشاط الجاري",
                        "code": "revenue_current_operation",
                        "amount_current_period": revenue_current,
                        "amount_previous_period": revenue_previous,
                    },
                    {
                        "name": "تكلفة النشاط الجاري",
                        "code": "cost_current_operation",
                        "amount_current_period": -abs(cost_current),
                        "amount_previous_period": -abs(cost_previous),
                    },
                ],
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
