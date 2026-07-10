"""
template_service.py
====================
CRUD operations for DocumentTemplate records.
Handles file uploads, default management, and seeding from demo.html.
"""
from __future__ import annotations

import os
import shutil
import uuid
from pathlib import Path

from flask import current_app
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.document_template import DocumentTemplate, DocumentTemplateType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _templates_upload_dir() -> Path:
    """Returns the directory where uploaded PDF backgrounds are stored."""
    upload_dir = Path(current_app.static_folder) / "templates" / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def _html_templates_dir() -> Path:
    """Returns the directory where user-created HTML templates are stored."""
    tpl_dir = Path(current_app.static_folder) / "templates" / "html"
    tpl_dir.mkdir(parents=True, exist_ok=True)
    return tpl_dir


def _demo_html_content() -> str:
    """Reads the built-in demo.html template as a starting point."""
    demo_path = Path(current_app.static_folder) / "templates" / "demo.html"
    if demo_path.exists():
        return demo_path.read_text(encoding="utf-8")
    return "<h1>Factura</h1><p>Plantilla sin contenido.</p>"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class TemplateService:

    @staticmethod
    def list_for_company(company_id: int) -> list[DocumentTemplate]:
        return (
            DocumentTemplate.query
            .filter_by(company_id=company_id)
            .order_by(DocumentTemplate.is_default.desc(), DocumentTemplate.id)
            .all()
        )

    @staticmethod
    def get(company_id: int, template_id: int) -> DocumentTemplate:
        return DocumentTemplate.query.filter_by(
            id=template_id, company_id=company_id
        ).first_or_404()

    @staticmethod
    def create(company_id: int, form_data, pdf_file=None) -> DocumentTemplate:
        tpl_type_str = form_data.get("type", DocumentTemplateType.html.value)
        tpl_type = DocumentTemplateType(tpl_type_str)

        tpl = DocumentTemplate(
            company_id=company_id,
            name=form_data.get("name", "Nueva plantilla").strip(),
            type=tpl_type,
            is_default=False,
        )

        if tpl_type == DocumentTemplateType.html:
            # Save the HTML content to a file
            html_content = form_data.get("html_content", _demo_html_content())
            filename = f"{uuid.uuid4().hex}.html"
            html_path = _html_templates_dir() / filename
            html_path.write_text(html_content, encoding="utf-8")
            tpl.html_template_path = f"html/{filename}"
        else:
            # PDF Overlay – save uploaded PDF background if provided
            import json
            if pdf_file and pdf_file.filename:
                safe = secure_filename(pdf_file.filename)
                dest_name = f"{uuid.uuid4().hex}_{safe}"
                dest = _templates_upload_dir() / dest_name
                pdf_file.save(str(dest))
                tpl.pdf_background_path = f"uploads/{dest_name}"

            coords_json = form_data.get("pdf_coordinates_json", "{}")
            try:
                tpl.pdf_coordinates = json.loads(coords_json)
            except Exception:
                tpl.pdf_coordinates = {}

        db.session.add(tpl)
        db.session.flush()

        # Auto-set as default if it's the first template for this company
        count = DocumentTemplate.query.filter_by(company_id=company_id).count()
        if count == 1:
            tpl.is_default = True

        db.session.commit()
        return tpl

    @staticmethod
    def update(company_id: int, template_id: int, form_data, pdf_file=None) -> DocumentTemplate:
        import json
        tpl = TemplateService.get(company_id, template_id)
        tpl.name = form_data.get("name", tpl.name).strip()

        if tpl.type == DocumentTemplateType.html:
            html_content = form_data.get("html_content", "")
            if html_content:
                # Write to existing file or create new
                if tpl.html_template_path:
                    html_path = Path(current_app.static_folder) / "templates" / tpl.html_template_path
                else:
                    filename = f"{uuid.uuid4().hex}.html"
                    html_path = _html_templates_dir() / filename
                    tpl.html_template_path = f"html/{filename}"
                html_path.write_text(html_content, encoding="utf-8")
        else:
            if pdf_file and pdf_file.filename:
                safe = secure_filename(pdf_file.filename)
                dest_name = f"{uuid.uuid4().hex}_{safe}"
                dest = _templates_upload_dir() / dest_name
                pdf_file.save(str(dest))
                # Remove old file
                if tpl.pdf_background_path:
                    old = Path(current_app.static_folder) / "templates" / tpl.pdf_background_path
                    if old.exists():
                        old.unlink(missing_ok=True)
                tpl.pdf_background_path = f"uploads/{dest_name}"

            coords_json = form_data.get("pdf_coordinates_json", "")
            if coords_json:
                try:
                    tpl.pdf_coordinates = json.loads(coords_json)
                except Exception:
                    pass

        db.session.commit()
        return tpl

    @staticmethod
    def set_default(company_id: int, template_id: int) -> DocumentTemplate:
        # Unset all defaults for this company
        DocumentTemplate.query.filter_by(company_id=company_id, is_default=True).update(
            {"is_default": False}
        )
        tpl = TemplateService.get(company_id, template_id)
        tpl.is_default = True
        db.session.commit()
        return tpl

    @staticmethod
    def delete(company_id: int, template_id: int) -> None:
        tpl = TemplateService.get(company_id, template_id)

        # Clean up files
        if tpl.html_template_path:
            html_path = Path(current_app.static_folder) / "templates" / tpl.html_template_path
            html_path.unlink(missing_ok=True)
        if tpl.pdf_background_path:
            pdf_path = Path(current_app.static_folder) / "templates" / tpl.pdf_background_path
            pdf_path.unlink(missing_ok=True)

        was_default = tpl.is_default
        db.session.delete(tpl)
        db.session.flush()

        # Re-assign default to next available template
        if was_default:
            next_tpl = DocumentTemplate.query.filter_by(company_id=company_id).first()
            if next_tpl:
                next_tpl.is_default = True

        db.session.commit()

    @staticmethod
    def read_html_content(tpl: DocumentTemplate) -> str:
        """Returns the HTML source of a template for editing."""
        if tpl.html_template_path:
            path = Path(current_app.static_folder) / "templates" / tpl.html_template_path
            if path.exists():
                return path.read_text(encoding="utf-8")
        return _demo_html_content()

    @staticmethod
    def get_default_coords() -> dict:
        """Returns the default PDF overlay coordinate structure."""
        from app.invoices.services.invoice_pdf_service import (
            HeaderCoords, ClientCoords, ItemsCoords, TotalsCoords
        )
        import dataclasses
        return {
            "header": dataclasses.asdict(HeaderCoords()),
            "client": dataclasses.asdict(ClientCoords()),
            "items":  dataclasses.asdict(ItemsCoords()),
            "totals": dataclasses.asdict(TotalsCoords()),
        }
