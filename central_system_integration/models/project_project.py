# -*- coding: utf-8 -*-

from odoo import models, fields

class ProjectProject(models.Model):
    _inherit = 'project.project'
    
    location = fields.Char()
    project_type = fields.Char()
    contracting_party = fields.Char()
    contractor = fields.Char()
    expected_number_of_hours = fields.Char()
    number_of_hours_consumed = fields.Char()
    
