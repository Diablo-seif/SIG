# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    commercial_register = fields.Char()
    nationality = fields.Selection([("egyptian", "Egyptian"), ("other", "other")], default='egyptian')
    passport = fields.Char()
