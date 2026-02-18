"""TNA Report"""
from collections import defaultdict

from odoo import api, models


# pylint: disable=protected-access
class TnaReport(models.AbstractModel):
    """TNA Report"""

    _name = "report.hr_tna.tna_report"

    # pylint: disable=unused-argument
    @api.model
    def _get_report_values(self, docids, data=None):
        """:return: dict: values of report data"""
        report_obj = self.env["ir.actions.report"]
        report = report_obj._get_report_from_name(
            "hr_tna.tna_report"
        )
        tnas = self.env["hr.tna"].browse(docids)
        tnas_details = []
        for tna in tnas:
            dept_groups = defaultdict(
                lambda: {
                    "planned_total_budget": 0,
                    "approved_total_budget": 0,
                    "lines": [],
                }
            )
            for line in tna.tna_line_ids:
                dept_groups[line.department_id].get("lines").append(line)
                dept_groups[line.department_id][
                    "planned_total_budget"
                ] += line.planned_budget
                dept_groups[line.department_id][
                    "approved_total_budget"
                ] += line.approved_budget
            tnas_details.append({
                "departments_groups": dept_groups,
                "tna": tna
            })

        docargs = {
            "doc_ids": self.ids,
            "doc_model": report.model,
            "docs": tnas_details,
        }
        return docargs
