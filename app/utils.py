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

def export_excel_response(filename: str, headers: list[str], rows: list[list]):
    """
    Generates an Excel file response.
    """
    import openpyxl
    from io import BytesIO
    from flask import Response
    from openpyxl.styles import Font

    wb = openpyxl.Workbook()
    ws = wb.active
    
    # Write headers
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)
        
    # Write rows
    for row in rows:
        ws.append(row)
        
    out = BytesIO()
    wb.save(out)
    out.seek(0)
    
    return Response(
        out.getvalue(),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-disposition': f'attachment; filename={filename}.xlsx'}
    )
