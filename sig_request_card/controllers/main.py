from odoo import http
from odoo.http import request
import base64
from odoo.exceptions import ValidationError
import io
from io import BytesIO
import xlsxwriter
import zipfile
from PIL import Image
import logging

_logger = logging.getLogger(__name__)


class RequestCardController(http.Controller):

    @http.route(["/my/request-card"], type="http", auth="public", website=True)
    def portal_request_card_form(self, **post):
        values = {
            "governorates": request.env["request.card.governorate"].sudo().search([]),
            "grades": request.env["sig.job.grade"].sudo().search([]),
            "positions": request.env["sig.job.position"]
            .sudo()
            .search([("for_organization", "=", "alshar_alaqari")]),
            "post": {},
        }
        return request.render("sig_request_card.portal_request_card_form", values)

    @http.route(
        ["/my/request-card/submit"], type="http", auth="public", website=True, csrf=True
    )
    def portal_request_card_submit(self, **post):
        vals = {
            "full_name": post.get("full_name"),
            "national_id": post.get("national_id"),
            "job_position_id": int(post.get("job_position_id")),
            "job_grade_id": int(post.get("job_grade_id")),
            "job_code": post.get("job_code"),
            "phone_number": post.get("phone_number"),
            "governorate_id": (
                int(post.get("governorate_id")) if post.get("governorate_id") else False
            ),
            "for_organization": "alshar_alaqari",
        }

        # Handle image if uploaded
        image_file = post.get("image")
        if image_file and hasattr(image_file, "read"):
            vals["image"] = base64.b64encode(image_file.read())

        try:
            self.check_national_id(vals["national_id"])
            self.check_phone_number(vals["phone_number"])
            request.env["sig.request.cards"].with_context(
                allow_create_by_code=True
            ).sudo().create(vals)
            return request.render("sig_request_card.portal_request_card_success")
        except ValidationError as e:
            values = {
                "governorates": request.env["request.card.governorate"]
                .sudo()
                .search([]),
                "grades": request.env["sig.job.grade"].sudo().search([]),
                "positions": request.env["sig.job.position"]
                .sudo()
                .search([("for_organization", "=", "alshar_alaqari")]),
                "error": str(e),
                "post": post,
            }
            return request.render("sig_request_card.portal_request_card_form", values)

    @http.route("/export/request/cards", type="http", auth="user")
    def export_request_cards(self, **kwargs):
        record_ids = [int(i) for i in kwargs.get("ids", "").split(",") if i]
        records = request.env["sig.request.cards"].sudo().browse(record_ids)
        separate_images = kwargs.get("separate_images") == "1"

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        worksheet = workbook.add_worksheet("Request Cards")

        worksheet.set_column(0, 7, 30)
        body_style = workbook.add_format(
            {"align": "center", "valign": "vcenter", "border": 1}
        )
        header_style = workbook.add_format(
            {
                "bold": True,
                "font_size": 12,
                "align": "center",
                "valign": "vcenter",
                "border": 1,
            }
        )

        headers = [
            "الاسم بالكامل",
            "الرقم القومي",
            "الدرجة الوظيفية",
            "الوظيفة",
            "الكود الوظيفي",
            "رقم الهاتف",
            "المحافظة",
        ]
        if not separate_images:
            headers.append("الصورة")
        else:
            zip_buffer = BytesIO()
            zip_file = zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED)
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_style)

        row = 1
        for rec in records:
            worksheet.write(row, 0, rec.full_name or "", body_style)
            worksheet.write(row, 1, rec.national_id or "", body_style)
            worksheet.write(row, 2, rec.job_grade_id.name or "", body_style)
            worksheet.write(row, 3, rec.job_position_id.name or "", body_style)
            worksheet.write(row, 4, rec.job_code or "", body_style)
            worksheet.write(row, 5, rec.phone_number or "", body_style)
            worksheet.write(
                row,
                6,
                rec.governorate_id.name if rec.governorate_id else "",
                body_style,
            )

            if not separate_images:
                worksheet.write(row, 7, "", body_style)
                if rec.image:
                    try:
                        image_data = base64.b64decode(rec.image)
                        image_stream = io.BytesIO(image_data)

                        # Open with Pillow to convert and ensure format
                        image_obj = Image.open(image_stream).convert("RGB")
                        final_image_stream = io.BytesIO()
                        image_obj.save(final_image_stream, format="PNG")
                        final_image_stream.seek(0)

                        worksheet.set_row(row, 150)
                        worksheet.insert_image(
                            row,
                            7,
                            "image.png",
                            {
                                "image_data": final_image_stream,
                                "x_scale": 0.25,
                                "y_scale": 0.25,
                                "x_offset": 2,
                                "y_offset": 2,
                            },
                        )
                    except Exception as e:
                        _logger.warning(
                            f"Failed to process image for record {rec.id}: {e}"
                        )
            else:
                if rec.image and rec.national_id:
                    image_data = base64.b64decode(rec.image)
                    image_filename = f"{rec.national_id}.png"
                    zip_file.writestr(image_filename, image_data)
            row += 1

        workbook.close()
        output.seek(0)
        if separate_images:
            zip_file.writestr("RequestCards.xlsx", output.read())
            zip_file.close()
            zip_buffer.seek(0)

            return request.make_response(
                zip_buffer.read(),
                headers=[
                    ("Content-Type", "application/zip"),
                    ("Content-Disposition", 'attachment; filename="RequestCards.zip"'),
                ],
            )
        else:
            filecontent = output.read()
            filename = "Request_Cards.xlsx"

            return request.make_response(
                filecontent,
                headers=[
                    (
                        "Content-Type",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    ),
                    ("Content-Disposition", f'attachment; filename="{filename}"'),
                ],
            )

    def check_national_id(self, national_id):
        if national_id and len(national_id) != 14:
            raise ValidationError("الرقم القومي يجب أن يتكون من ١٤ رقمًا بالضبط")
        if national_id and national_id[0] not in ["2", "3"]:
            raise ValidationError("الرقم القومي يجب أن يبدأ بالرقم ٢ أو ٣")

    def check_phone_number(self, phone_number):
        if len(phone_number) != 11:
            raise ValidationError("رقم الهاتف يجب أن يتكون من ١١ رقمًا بالضبط")

    @http.route(
        ["/my/request-card-el_mesaha_el_Askareya"],
        type="http",
        auth="public",
        website=True,
    )
    def portal_request_card_form_el_mesaha_el_Askareya(self, **post):
        values = {
            "governorates": request.env["request.card.governorate"].sudo().search([]),
            "companies": request.env["associated.company"].sudo().search([]),
            "positions": request.env["sig.job.position"]
            .sudo()
            .search([("for_organization", "=", "el_mesaha_el_Askareya")]),
            "post": {},
        }
        return request.render(
            "sig_request_card.portal_request_card_form_el_mesaha_el_Askareya", values
        )

    @http.route(
        ["/my/request-card-el_mesaha_el_Askareya/submit"],
        type="http",
        auth="public",
        website=True,
        csrf=True,
    )
    def portal_request_card_submit_el_mesaha_el_Askareya(self, **post):
        vals = {
            "full_name": post.get("full_name"),
            "national_id": post.get("national_id"),
            "job_position_id": int(post.get("job_position_id")),
            "associated_company_id": int(post.get("associated_company_id")),
            # "job_grade_id": int(post.get("job_grade_id")),
            "job_code": post.get("job_code"),
            "phone_number": post.get("phone_number"),
            "governorate_id": (
                int(post.get("governorate_id")) if post.get("governorate_id") else False
            ),
            "for_organization": "el_mesaha_el_Askareya",
        }

        # Handle image if uploaded
        image_file = post.get("image")
        if image_file and hasattr(image_file, "read"):
            vals["image"] = base64.b64encode(image_file.read())

        try:
            self.check_national_id(vals["national_id"])
            self.check_phone_number(vals["phone_number"])
            request.env["sig.request.cards"].with_context(
                allow_create_by_code=True
            ).sudo().create(vals)
            return request.render("sig_request_card.portal_request_card_success")
        except ValidationError as e:
            values = {
                "governorates": request.env["request.card.governorate"]
                .sudo()
                .search([]),
                # "grades": request.env["sig.job.grade"].sudo().search([]),
                "positions": request.env["sig.job.position"]
                .sudo()
                .search([("for_organization", "=", "el_mesaha_el_Askareya")]),
                "error": str(e),
                "post": post,
            }
            return request.render(
                "sig_request_card.portal_request_card_form_el_mesaha_el_Askareya",
                values,
            )
