"""Compatibility loader for accounting route modules.

Routes are grouped by domain in :mod:`app.accounting.views`.
"""

from . import views  # noqa: F401

__all__ = ["views"]
