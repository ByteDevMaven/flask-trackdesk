"""
Internal date / file helpers shared across accounting services.
"""
import os
import uuid
from datetime import datetime, UTC

from flask import current_app


def _allowed_file(filename: str) -> bool:
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'png', 'jpg', 'jpeg', 'webp'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


def _save_receipt(file) -> str | None:
    """Save uploaded receipt; return relative URL or None."""
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
