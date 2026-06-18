"""
Internal date / file helpers shared across accounting services.
"""
import os
import uuid
import mimetypes
from datetime import datetime, UTC

from flask import current_app


def _allowed_file(filename: str) -> bool:
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'png', 'jpg', 'jpeg', 'webp'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


def _save_receipt(file) -> str | None:
    """Save a single uploaded receipt; return relative URL or None.

    Kept for legacy backward-compatibility (old single-file expense path).
    New code should use _save_attachments() instead.
    """
    if not file or file.filename == '':
        return None
    if not _allowed_file(file.filename):
        return None
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    upload_dir = os.path.join(current_app.config.get('UPLOAD_FOLDER', ''), 'receipts')
    os.makedirs(upload_dir, exist_ok=True)
    file.save(os.path.join(upload_dir, unique_name))
    return f"uploads/receipts/{unique_name}"


def _save_attachments(files_list, reference_type: str, reference_id: int,
                      company_id: int, user_id: int | None = None) -> list:
    """Save multiple uploaded files and return a list of AccountingAttachment instances.

    Files are stored in static/uploads/receipts/ — the same directory used by the
    legacy receipt_url field — so existing files remain accessible without any URL changes.

    Args:
        files_list: iterable of werkzeug FileStorage objects (may be empty).
        reference_type: 'Expense' | 'Income' | 'Journal'
        reference_id: PK of the parent record.
        company_id: owning company.
        user_id: optional FK of the uploading user.

    Returns:
        List of unsaved AccountingAttachment instances (caller must add to session).
    """
    from app.models.accounting_attachment import AccountingAttachment

    attachments = []
    upload_dir = os.path.join(current_app.config.get('UPLOAD_FOLDER', ''), 'receipts')
    os.makedirs(upload_dir, exist_ok=True)

    for file in (files_list or []):
        if not file or not getattr(file, 'filename', None) or file.filename == '':
            continue
        if not _allowed_file(file.filename):
            current_app.logger.warning(
                '_save_attachments: skipping disallowed file type filename=%r', file.filename
            )
            continue

        ext = file.filename.rsplit('.', 1)[1].lower()
        original_name = os.path.basename(file.filename)
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        dest_path = os.path.join(upload_dir, unique_name)

        # Read content once so we can measure size before saving
        content = file.read()
        file_size = len(content)
        with open(dest_path, 'wb') as fh:
            fh.write(content)

        mime_type = mimetypes.guess_type(original_name)[0] or ''
        rel_path = f"uploads/receipts/{unique_name}"

        att = AccountingAttachment(
            company_id=company_id,
            reference_type=reference_type,
            reference_id=reference_id,
            filename=original_name,
            file_path=rel_path,
            file_size=file_size,
            mime_type=mime_type,
            uploaded_at=datetime.now(UTC),
            uploaded_by=user_id,
        )
        attachments.append(att)

    return attachments


def _parse_date(date_str: str, default_now: bool = True) -> datetime:
    """Parse YYYY-MM-DD string → naive datetime. Falls back to now(UTC)."""
    if date_str:
        try:
            return datetime.strptime(date_str.strip(), '%Y-%m-%d')
        except ValueError:
            pass
    return datetime.now(UTC).replace(tzinfo=None) if default_now else None


def _make_naive(dt: datetime) -> datetime:
    """Strip timezone info so comparisons work with our stored naive datetimes."""
    if dt is None:
        return dt
    return dt.replace(tzinfo=None) if dt.tzinfo else dt


def _get_period_bounds(start_date: str, end_date: str):
    """Return (start_dt, end_dt) as naive datetimes for the given period."""
    now = _make_naive(datetime.now(UTC))
    start_dt = _parse_date(start_date) if start_date else now.replace(day=1, hour=0, minute=0, second=0)
    raw_end = _parse_date(end_date) if end_date else now
    end_dt = raw_end.replace(hour=23, minute=59, second=59)
    return _make_naive(start_dt), _make_naive(end_dt)
