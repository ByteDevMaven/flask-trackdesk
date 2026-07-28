from flask import render_template, request, jsonify, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.models import db, ApprovalRequest, ApprovalStatus
from app.utils import resolve_company
from app.services.approval_service import ApprovalService
from . import approvals_bp

@approvals_bp.route('/<string:company_id>/approvals')
@login_required
def index(company_id):
    if not current_user.has_permission('approvals.manage'):
        abort(403)
    company = resolve_company(company_id)
    pending = ApprovalService.get_pending_requests(company.id)
    history = ApprovalService.get_resolved_requests(company.id)
    return render_template('approvals/index.html', requests=pending, history=history, company_id=company_id)

@approvals_bp.route('/api/<string:company_id>/approvals/<int:id>/approve', methods=['POST'])
@login_required
def approve(company_id, id):
    if not current_user.has_permission('approvals.manage'):
        abort(403)
    company = resolve_company(company_id)
    try:
        req = ApprovalService.approve_request(id, current_user.id, company.id)
        return jsonify({'success': True, 'message': 'Aprobado correctamente.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@approvals_bp.route('/api/<string:company_id>/approvals/<int:id>/reject', methods=['POST'])
@login_required
def reject(company_id, id):
    if not current_user.has_permission('approvals.manage'):
        abort(403)
    company = resolve_company(company_id)
    try:
        req = ApprovalService.reject_request(id, current_user.id, company.id)
        return jsonify({'success': True, 'message': 'Rechazado correctamente.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
