""" init hr evaluation portal """
import re
from collections import OrderedDict
from operator import itemgetter

from odoo import _, http
from odoo.addons.portal.controllers.portal import (
    CustomerPortal,
    pager as portal_pager,
)
from odoo.exceptions import (
    AccessDenied, AccessError, MissingError, UserError,
    ValidationError,
)
from odoo.http import request
from odoo.osv.expression import OR
from odoo.tools import groupby as groupbyelem


class HrEvaluationPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'evaluation_count' in counters:
            values['evaluation_count'] = \
                request.env['hr.evaluation'].search_count([])
        return values

    # ------------------------------------------------------------
    # My Evaluation
    # ------------------------------------------------------------
    def _evaluation_get_page_view_values(self, evaluation, access_token,
                                         **kwargs):
        values = {
            'page_name': 'evaluation',
            'evaluation': evaluation,
            'user': request.env.user
        }
        return self._get_page_view_values(
            evaluation, access_token, values,
            'my_evaluations_history', False, **kwargs)

    @http.route(['/my/evaluations', '/my/evaluations/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_my_evaluations(self, page=1, date_begin=None, date_end=None,
                              sortby=None, filterby=None, search=None,
                              search_in='content', groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'start_date desc'},
            'name': {'label': _('Number'), 'order': 'name'},
            'state': {'label': _('Status'), 'order': 'state'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }
        searchbar_inputs = {
            'content': {
                'input': 'content', 'label': _(
                    'Search <span class="nolabel"> (in Content)</span>')
            },
            'state': {'input': 'state', 'label': _('Search in Status')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'state': {'input': 'state', 'label': _('Status')},
        }

        # extends filterby criteria with project the customer has access to
        periods = request.env['hr.evaluation.period'].search([])
        for period in periods:
            searchbar_filters.update({
                str(period.id): {
                    'label': period.name,
                    'domain': [('period_id', '=', period.id)]
                }
            })

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters.get(filterby, searchbar_filters.get('all'))[
            'domain']

        # default group by value
        if not groupby:
            groupby = 'state'

        if date_begin and date_end:
            domain += [('start_date', '>', date_begin),
                       ('start_date', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('content', 'all'):
                search_domain = \
                    OR([search_domain,
                        [
                            '|',
                            ('performance_line_ids.name', 'ilike', search),
                            ('performance_line_ids.description', 'ilike',
                             search),
                        ]])
            if search_in in ('state', 'all'):
                search_domain = OR(
                    [search_domain, [('state', 'ilike', search)]])
            domain += search_domain

        # evaluation count
        evaluation_count = request.env['hr.evaluation'].search_count(domain)
        print(
            "================================ evaluation_count =============================")
        print(evaluation_count)
        # pager
        pager = portal_pager(
            url="/my/evaluations",
            url_args={
                'date_begin': date_begin, 'date_end': date_end,
                'sortby': sortby, 'filterby': filterby,
                'groupby': groupby, 'search_in': search_in,
                'search': search
            },
            total=evaluation_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        if groupby == 'period':
            order = "period_id, %s" % order
            # force sort on project first to group by project in view
        elif groupby == 'state':
            order = "state, %s" % order
            # force sort on stage first to group by stage in view

        evaluations = request.env['hr.evaluation'].search(domain, order=order,
                                                          limit=self._items_per_page,
                                                          offset=pager[
                                                              'offset'])
        request.session['my_evaluations_history'] = evaluations.ids[:100]
        print(
            "============================= evaluations ============================")
        print(evaluations)

        if groupby == 'period_id':
            grouped_evaluations = [request.env['hr.evaluation'].concat(*g) for
                                   k, g in
                                   groupbyelem(evaluations,
                                               itemgetter('period_id'))]
        elif groupby == 'state':
            grouped_evaluations = [request.env['hr.evaluation'].concat(*g) for
                                   k, g in
                                   groupbyelem(evaluations,
                                               itemgetter('state'))]
        else:
            grouped_evaluations = [evaluations]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_evaluations': grouped_evaluations,
            'page_name': 'evaluation',
            'default_url': '/my/evaluations',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("hr_performance_evaluation.portal_my_evaluations",
                              values)

    @http.route(['/my/evaluation/<int:evaluation_id>'], type='http',
                auth="public",
                website=True)
    def portal_my_evaluation(self, evaluation_id, access_token=None, **kw):
        try:
            evaluation_sudo = self._document_check_access(
                'hr.evaluation', evaluation_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._evaluation_get_page_view_values(
            evaluation_sudo, access_token, **kw)
        return request.render(
            "hr_performance_evaluation.portal_my_evaluation", values)

    @http.route(['/my/evaluation/<int:evaluation_id>/edit'], type='http',
                auth="user", website=True)
    def portal_my_evaluation_edit(self, evaluation_id, access_token=None, **kw):
        try:
            evaluation_sudo = self._document_check_access(
                'hr.evaluation', evaluation_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my/evaluation/%s' % evaluation_id)
        values = self._evaluation_get_page_view_values(
            evaluation_sudo, access_token, **kw)
        if request.httprequest.method == 'GET':
            return request.render(
                "hr_performance_evaluation.portal_my_evaluation_edit", values)
        if request.httprequest.method == 'POST':
            for id_str, date_str in kw.items():
                performance_to_update = {}
                line_id = False
                # find possible integer in string
                line_ids = re.findall('[0-9]+', id_str)
                if line_ids:
                    line_id = int(line_ids[0])

                if 'performance_line_ids' in id_str and line_id:
                    if 'final_rating' in id_str:
                        performance_to_update.update({
                            'final_rating': date_str and date_str / 100 or 0,
                        })
                    elif 'final_remark' in id_str:
                        performance_to_update.update({
                            'final_remark': date_str.strip(),
                        })
                if performance_to_update and line_id:
                    try:
                        evaluation_sudo.write({
                            'performance_line_ids': [
                                (1, line_id, performance_to_update)]
                        })
                        if evaluation_sudo.state == 'send_to_manager' and not evaluation_sudo.manager_done_evaluation:
                            evaluation_sudo.action_done()
                    except (ValidationError, UserError) as e:
                        values['error'] = e
                        request.env.cr.rollback()

                    except AccessDenied as e:
                        values['error'] = _('Only employee and manager can '
                                            'update document. Please contact '
                                            'the administrator.')
                        request.env.cr.rollback()
            print('==================================================')
            print(values)
            if 'error' in values:
                return request.render(
                    "hr_performance_evaluation.portal_my_evaluation_edit",
                    values)
            else:
                return request.redirect(
                    '/my/evaluation/%s' % evaluation_sudo.id)
