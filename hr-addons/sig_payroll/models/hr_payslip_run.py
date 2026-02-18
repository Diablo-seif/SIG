
from odoo import models, fields, api


class HrPayslipRun(models.Model):

    _inherit = 'hr.payslip.run'
    
    proposal_id = fields.Many2one(
        'proposal.proposal',
        domain=[('is_outsourcing', '=', True)]
    )
    
    def action_payslip_done(self):
        journal = self.env['account.journal'].sudo().search([('code', '=', 'SLR')], limit=1)
        move_dict = {
            'narration': '',
            'ref': fields.Date().end_of(self.date_end, 'month').strftime('%B %Y'),
            'proposal_id': self.proposal_id.id,
             'journal_id': journal.id,
            'date': self.date_end,
        }
        lines = []
        rules = self.env['hr.salary.rule'].sudo().search([
            # '|',
            # ('account_debit', '!=', False),
            # ('account_credit', '!=', False)
            ])
        total_debit = 0
        total_credit = 0
        
        for rule in rules:
            total = 0
            slips_lines = self.env['hr.payslip.line'].sudo().search(
            [('slip_id', 'in', self.slip_ids.ids),
                ('salary_rule_id', '=', rule.id)])
            for line in slips_lines:
                total += line.total
                
            if rule.account_credit:
                total_credit += total
                lines.append({
                    'name': rule.name,
                    'account_id': rule.account_credit.id,
                    'journal_id': rule.struct_id.journal_id.id,
                    'date': self.date_end,
                    'debit': 0,
                    'credit': total,
                })
            if rule.account_debit:
                total_debit += total
                lines.append({
                        'name': rule.name,
                        'account_id': rule.account_debit.id,
                        'journal_id': rule.struct_id.journal_id.id,
                        'date': self.date_end,
                        'debit': total,
                        'credit': 0,
                    })
        if total_debit > total_credit:
            lines.append({
                'name': 'Adjustment Entry',
                'account_id': rule.struct_id.journal_id.default_account_id.id,
                'journal_id': rule.struct_id.journal_id.id,
                'date': self.date_end,
                'debit': total_debit - total_credit,
                'credit': 0,
            })
        elif total_debit < total_credit:
            lines.append({
                'name': 'Adjustment Entry',
                'account_id': rule.struct_id.journal_id.default_account_id.id,
                'journal_id': rule.struct_id.journal_id.id,
                'date': self.date_end,
                'credit': total_debit - total_credit,
                'debit': 0,
            })
        move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in lines]
        self.env['account.move'].sudo().create(move_dict)
        self.state = 'close'