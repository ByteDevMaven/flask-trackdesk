from datetime import datetime, UTC

from flask import jsonify, redirect, render_template, request, url_for, flash
from flask_login import current_user, login_required

from app.models import Company, Notification, User, db

from . import notifications


def _can_send_notifications():
    return bool(
        current_user.is_authenticated
        and (
            current_user.is_superadmin
            or current_user.has_permission('users.manage')
        )
    )


def _visible_users():
    if current_user.is_superadmin:
        return User.query.order_by(User.name).all()

    visible_ids = {company.id for company in current_user.companies}
    if not visible_ids:
        return [current_user]

    return (
        User.query
        .filter(User.companies.any(Company.id.in_(visible_ids)))
        .order_by(User.name)
        .all()
    )


def _visible_companies():
    if current_user.is_superadmin:
        return Company.query.order_by(Company.name).all()
    return sorted(current_user.companies, key=lambda company: company.name.lower())


def _serialize(notification):
    created_at = notification.sent_at or notification.created_at
    return {
        'id': notification.id,
        'title': notification.title,
        'body': notification.display_body,
        'type': notification.type,
        'priority': notification.priority,
        'status': notification.status,
        'is_popup': bool(notification.is_popup),
        'link_url': notification.link_url,
        'sent_at': created_at.isoformat() if created_at else None,
    }


def _query_current_user_notifications(include_read=True):
    query = Notification.query.filter(Notification.user_id == current_user.id)
    now = datetime.now(UTC)
    query = query.filter((Notification.expires_at.is_(None)) | (Notification.expires_at > now))
    if not include_read:
        query = query.filter(Notification.status == 'unread', Notification.read_at.is_(None))
    return query


@notifications.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')

    query = _query_current_user_notifications(include_read=True)
    if status == 'unread':
        query = query.filter(Notification.status == 'unread', Notification.read_at.is_(None))
    elif status == 'read':
        query = query.filter(Notification.status == 'read')

    pagination = (
        query
        .order_by(Notification.sent_at.desc(), Notification.created_at.desc())
        .paginate(page=page, per_page=20)
    )

    unread_count = _query_current_user_notifications(include_read=False).count()
    sent_notifications = []
    if _can_send_notifications():
        sent_notifications = (
            Notification.query
            .filter(Notification.created_by_id == current_user.id)
            .order_by(Notification.sent_at.desc(), Notification.created_at.desc())
            .limit(15)
            .all()
        )

    return render_template(
        'notifications/index.html',
        notifications=pagination.items,
        pagination=pagination,
        status=status,
        unread_count=unread_count,
        can_send=_can_send_notifications(),
        users=_visible_users() if _can_send_notifications() else [],
        companies=_visible_companies() if _can_send_notifications() else [],
        sent_notifications=sent_notifications,
    )


@notifications.route('/send', methods=['POST'])
@login_required
def send():
    if not _can_send_notifications():
        flash('No tienes permiso para enviar notificaciones.', 'error')
        return redirect(url_for('notifications.index'))

    title = request.form.get('title', '').strip()
    body = request.form.get('body', '').strip()
    notification_type = request.form.get('type', 'info').strip() or 'info'
    priority = request.form.get('priority', 'normal').strip() or 'normal'
    link_url = request.form.get('link_url', '').strip() or None
    is_popup = bool(request.form.get('is_popup'))
    target = request.form.get('target', 'users')
    selected_user_ids = [int(user_id) for user_id in request.form.getlist('user_ids') if user_id.isdigit()]
    selected_company_id = request.form.get('company_id', type=int)

    if not title or not body:
        flash('Titulo y mensaje son requeridos.', 'error')
        return redirect(url_for('notifications.index'))

    visible_user_ids = {user.id for user in _visible_users()}
    recipient_ids = set()
    company_id = None

    if target == 'all':
        recipient_ids = visible_user_ids
    elif target == 'company' and selected_company_id:
        company_ids = {company.id for company in _visible_companies()}
        if selected_company_id in company_ids:
            company_id = selected_company_id
            users = User.query.filter(User.companies.any(Company.id == selected_company_id)).all()
            recipient_ids = {user.id for user in users if user.id in visible_user_ids}
    else:
        recipient_ids = {user_id for user_id in selected_user_ids if user_id in visible_user_ids}

    if not recipient_ids:
        flash('Selecciona al menos un destinatario valido.', 'error')
        return redirect(url_for('notifications.index'))

    sent_at = datetime.now(UTC)
    for user_id in recipient_ids:
        db.session.add(Notification(
            user_id=user_id,
            company_id=company_id,
            created_by_id=current_user.id,
            type=notification_type,
            title=title,
            message=body,
            body=body,
            link_url=link_url,
            priority=priority,
            channel='in_app',
            status='unread',
            is_popup=is_popup,
            sent_at=sent_at,
        ))

    db.session.commit()
    flash(f'Notificacion enviada a {len(recipient_ids)} usuario(s).', 'success')
    return redirect(url_for('notifications.index'))


@notifications.route('/api/recent')
@login_required
def recent():
    items = (
        _query_current_user_notifications(include_read=True)
        .order_by(Notification.sent_at.desc(), Notification.created_at.desc())
        .limit(8)
        .all()
    )
    unread_count = _query_current_user_notifications(include_read=False).count()
    return jsonify({
        'unread_count': unread_count,
        'notifications': [_serialize(item) for item in items],
    })


@notifications.route('/api/popups')
@login_required
def popups():
    items = (
        _query_current_user_notifications(include_read=False)
        .filter(Notification.is_popup.is_(True))
        .order_by(Notification.sent_at.desc(), Notification.created_at.desc())
        .limit(3)
        .all()
    )
    return jsonify({'notifications': [_serialize(item) for item in items]})


@notifications.route('/api/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_read(notification_id):
    notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first_or_404()
    notification.status = 'read'
    notification.read_at = datetime.now(UTC)
    db.session.commit()
    return jsonify({'success': True})


@notifications.route('/api/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    now = datetime.now(UTC)
    unread = _query_current_user_notifications(include_read=False).all()
    for notification in unread:
        notification.status = 'read'
        notification.read_at = now
    db.session.commit()
    return jsonify({'success': True, 'count': len(unread)})


@notifications.route('/api/<int:notification_id>/archive', methods=['POST'])
@login_required
def archive(notification_id):
    notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first_or_404()
    notification.status = 'archived'
    notification.read_at = notification.read_at or datetime.now(UTC)
    db.session.commit()
    return jsonify({'success': True})
