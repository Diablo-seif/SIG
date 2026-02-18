
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class RequestCard(models.Model):
    _name = 'sig.request.cards'
    _rec_name = 'full_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    full_name = fields.Char(required=True, tracking=True)
    national_id = fields.Char(size=14, string="National ID", tracking=True)
    job_position_id = fields.Many2one('sig.job.position', required=True, tracking=True)
    job_grade_id = fields.Many2one('sig.job.grade', tracking=True)
    job_code = fields.Char(tracking=True)
    phone_number = fields.Char(tracking=True)
    governorate_id = fields.Many2one('request.card.governorate', tracking=True)
    image = fields.Binary(tracking=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('in_review', 'In Review'),
        ('reviewed', 'Reviewed'),
        ('print', 'Print'),
        ('sent', 'Sent'),
        ('holding', 'Holding'),
        ('cancelled', 'Cancelled')
    ], default='draft', required=True, tracking=True)
    is_duplicate = fields.Boolean(compute='_compute_is_duplicate', store=True)
    for_organization = fields.Selection([
        ('alshar_alaqari', 'Al-Shahr Al-Aqari'),
        ('el_mesaha_el_Askareya', 'El-Mesaha El-Askareya'),
    ], default="alshar_alaqari")
    associated_company_id = fields.Many2one('associated.company')
    
    @api.model
    def create(self, vals):
        if not self.env.context.get('import_file') and not self.env.context.get('allow_create_by_code'):
            raise UserError("Manual creation is not allowed.")
        return super().create(vals)

    @api.constrains('national_id')
    def _check_national_id(self):
        for rec in self:
            if rec.national_id and len(rec.national_id) != 14:
                raise ValidationError('الرقم القومي يجب أن يتكون من ١٤ رقمًا بالضبط')
            if rec.national_id and rec.national_id[0] not in ['2', '3']:
                raise ValidationError('الرقم القومي يجب أن يبدأ بالرقم ٢ أو ٣')
            # existing_record = self.env['sig.request.cards'].sudo().search([('national_id', '=', rec.national_id),
            #                                                                ('id', '!=', rec.id)], limit=1)
            # if existing_record:
            #     raise ValidationError('يوجد بالفعل طلب كارت لهذا الرقم القومي')

    @api.constrains('phone_number')
    def _check_phone_number(self):
        for rec in self:
            if rec.phone_number and len(rec.phone_number) != 11:
                raise ValidationError('رقم الهاتف يجب أن يتكون من ١١ رقمًا بالضبط')

    @api.depends('national_id')
    def _compute_is_duplicate(self):
        for record in self:
            domain = [('national_id', '=', record.national_id)]
            if isinstance(record.id, int):
                domain.append(('id', '!=', record.id))
            existing_records = self.env['sig.request.cards'].sudo().search(domain)
            if len(existing_records) > 0:
                existing_records.write({'is_duplicate': True})
                record.is_duplicate = True
            else:
                record.is_duplicate = False

    def request_card_in_review(self):
        for record in self:
            if record.status not in ['draft', 'holding']:
                raise ValidationError('Only draft cards can be put in review')
            record.status = 'in_review'

    def request_card_hold(self):
        for record in self:
            if record.status not in ['in_review', 'draft', 'reviewed', 'print', 'cancelled']:
                raise ValidationError('Only draft, in review, reviewed, and printed cards can be held')
            record.status = 'holding'

    def request_card_cancelled(self):
        for record in self:
            if record.status not in ['in_review', 'draft', 'reviewed', 'holding']:
                raise ValidationError('Only draft, in review, and reviewed cards can be cancelled')
            record.status = 'cancelled'

    def request_card_reviewed(self):
        for record in self:
            if record.status not in ['in_review', 'holding']:
                raise ValidationError('Only in review cards can be reviewed')
            record.status = 'reviewed'

    def request_card_print(self):
        for record in self:
            if record.status not in ['reviewed', 'holding']:
                raise ValidationError('Only reviewed cards can be printed')
            record.status = 'print'

    def request_card_sent(self):
        for record in self:
            if record.status != 'print':
                raise ValidationError('Only printed cards can be sent')
            record.status = 'sent'

    def request_card_export_excel(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/export/request/cards?ids=%s&separate_images=0' % ','.join(map(str, self.ids)),
            'target': 'self',
        }

    def request_card_export_excel_separate_images(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/export/request/cards?ids=%s&separate_images=1' % ','.join(map(str, self.ids)),
            'target': 'self',
        }
