from datetime import UTC, datetime

from flask import flash, jsonify, make_response, redirect, render_template, request, url_for
from flask_login import login_required

from app.models import Account, Project, Tag, Transaction
from app.models.enums import AccountType, TransactionType
from app.utils import resolve_company

from .. import accounting
from ..services import AccountingService
from .common import _company_url_id, _is_ajax, _sidebar_ctx


@accounting.route('/<string:company_id>/accounting/')
@login_required
def index(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    data = AccountingService.get_dashboard_data(company_id)
    return render_template('accounting/dashboard.html', **data)
