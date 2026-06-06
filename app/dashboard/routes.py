from flask import render_template, session
from flask_login import login_required
from flask_babel import _

from . import dashboard
from .services import DashboardService


@dashboard.route('/')
@dashboard.route('/<int:company_id>/')
@dashboard.route('/<int:company_id>/dashboard')
@login_required
def index(company_id=None):
    if company_id is None:
        company_id = session.get('selected_company_id')

    data = DashboardService.get_dashboard_data(company_id)

    return render_template('dashboard/index.html', **data)


@dashboard.app_template_filter('format_currency')
def format_currency(value, decimals=2):
    """Format a number as currency"""
    if value is None:
        return f"0.{'0' * decimals}"
    return f"{float(value):,.{decimals}f}"


@dashboard.app_template_filter('format_date')
def format_date(value):
    """Format a date in a readable format"""
    if value is None:
        return ""
    return value.strftime("%b %d, %Y")


@dashboard.app_template_filter('locale_date')
def locale_date(value):
    """Format date according to the current locale"""
    from flask_babel import format_datetime

    if value is None:
        return ""

    try:
        return format_datetime(value, format='medium')
    except Exception:
        return value.strftime("%b %d, %Y")