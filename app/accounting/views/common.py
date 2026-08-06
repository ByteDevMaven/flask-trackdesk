from flask import request

from app.models.enums import AccountType


def _sidebar_ctx(company_id: int) -> dict:
    return {
        'company_id': company_id,
        'AccountType': AccountType,
    }


def _company_url_id(company) -> str:
    """URL segment for company-scoped routes (slug preferred, else numeric id)."""
    return company.slug if company.slug else str(company.id)


def _is_ajax() -> bool:
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'
