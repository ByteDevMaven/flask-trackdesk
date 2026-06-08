from flask_login import current_user
from flask import abort
from app.companies.services import CompanyService

def resolve_company(company_id_or_slug):
    """
    Helper to resolve a company from a route parameter that could be an integer ID or a slug.
    Checks user permissions via CompanyService.
    Returns the Company object.
    """
    if isinstance(company_id_or_slug, int) or (isinstance(company_id_or_slug, str) and company_id_or_slug.isdigit()):
        return CompanyService.get_company_for_user(int(company_id_or_slug), current_user)
    else:
        return CompanyService.get_company_by_slug(company_id_or_slug, current_user)
