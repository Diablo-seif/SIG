"""Man Power Plan Report"""

from collections import defaultdict

from odoo import api, models


# pylint: disable=protected-access
class ManPowerPlanReport(models.AbstractModel):
    """Man Power Plan Report"""

    _name = "report.hr_manpower_plan.report_manpower_planned"

    # pylint: disable=unused-argument
    @api.model
    def _get_report_values(self, docids, data=None):
        """:return: dict: values of report data"""
        report_obj = self.env["ir.actions.report"]
        report = report_obj._get_report_from_name(
            "hr_manpower_plan.report_manpower_planned"
        )
        manpowers = self.env["hr.manpower.plan"].browse(docids)
        manpowers_details = []
        for manpower in manpowers:
            dept_groups = defaultdict(
                lambda: {
                    "planned_total_budget": 0,
                    "approved_total_budget": 0,
                    "current_total_budget": 0,
                    "actual_total_budget": 0,
                    "lines": [],
                }
            )
            for line in manpower.manpower_line_ids:
                dept_groups[line.department_id].get("lines").append(line)
                dept_groups[line.department_id][
                    "planned_total_budget"
                ] += line.total_budget
                dept_groups[line.department_id][
                    "approved_total_budget"
                ] += line.approved_budget
                dept_groups[line.department_id][
                    "current_total_budget"
                ] += line.current_budget
                dept_groups[line.department_id][
                    "actual_total_budget"
                ] += line.actual_budget
            manpowers_details.append({
                "departments_groups": dept_groups,
                "manpower": manpower
            })

        docargs = {
            "doc_ids": self.ids,
            "doc_model": report.model,
            "docs": manpowers_details,
        }
        return docargs
