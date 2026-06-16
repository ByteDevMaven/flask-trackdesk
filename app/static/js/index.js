/**
 * index.js - Inicialización de componentes globales de UI.
 * Sin código Jinja. Sin event handlers inline.
 */

'use strict';

document.addEventListener('DOMContentLoaded', () => {

  const collapseBtn = document.getElementById('collapse-sidebar-btn');
  const expandBtn = document.getElementById('expand-sidebar-btn');
  const sidebar = document.getElementById('secondary-sidebar');

  if (collapseBtn && sidebar) {
    collapseBtn.addEventListener('click', () => {
      sidebar.classList.remove('w-56');
      sidebar.classList.add('w-0');
      if (expandBtn) {
        expandBtn.classList.remove('hidden');
        expandBtn.classList.add('flex');
      }
    });
  }

  if (expandBtn && sidebar) {
    expandBtn.addEventListener('click', () => {
      sidebar.classList.remove('w-0');
      sidebar.classList.add('w-56');
      expandBtn.classList.remove('flex');
      expandBtn.classList.add('hidden');
    });
  }

  const companyBtn = document.getElementById('company-menu-btn');
  const companyMenu = document.getElementById('company-menu');

  if (companyBtn && companyMenu) {
    companyBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      companyMenu.classList.toggle('hidden');
    });

    document.addEventListener('click', (e) => {
      if (!companyBtn.contains(e.target) && !companyMenu.contains(e.target)) {
        companyMenu.classList.add('hidden');
      }
    });
  }

  const userSettingsBtn = document.getElementById('user-settings-btn');
  const userSettingsMenu = document.getElementById('user-settings-menu');

  if (userSettingsBtn && userSettingsMenu) {
    userSettingsBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      userSettingsMenu.classList.toggle('hidden');
    });

    document.addEventListener('click', (e) => {
      if (!userSettingsBtn.contains(e.target) && !userSettingsMenu.contains(e.target)) {
        userSettingsMenu.classList.add('hidden');
      }
    });
  }

  const toastContainer = document.getElementById('toast-container');
  if (toastContainer) {
    toastContainer.addEventListener('click', (e) => {
      e.stopPropagation();
    });
    toastContainer.style.pointerEvents = 'auto';
  }

  const notificationWrapper = document.getElementById('notification-menu-wrapper');
  const notificationBtn = document.getElementById('notification-menu-btn');
  const notificationMenu = document.getElementById('notification-menu');
  const notificationList = document.getElementById('notification-list');
  const notificationBadge = document.getElementById('notification-badge');
  const notificationSubtitle = document.getElementById('notification-menu-subtitle');
  const notificationMarkAllBtn = document.getElementById('notification-mark-all-btn');
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || '';

  function endpoint(path) {
    const centerUrl = notificationWrapper?.dataset.centerUrl || '/notifications/';
    return `${centerUrl.replace(/\/$/, '')}${path}`;
  }

  function notificationTypeClass(type) {
    const classes = {
      success: 'bg-emerald-50 text-emerald-700',
      warning: 'bg-amber-50 text-amber-700',
      danger: 'bg-rose-50 text-rose-700',
      error: 'bg-rose-50 text-rose-700',
      info: 'bg-sky-50 text-sky-700'
    };
    return classes[type] || 'bg-slate-100 text-slate-600';
  }

  function postNotificationAction(url) {
    return fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      }
    });
  }

  function updateNotificationBadge(count) {
    if (!notificationBadge) return;
    if (count > 0) {
      notificationBadge.textContent = count > 9 ? '9+' : String(count);
      notificationBadge.classList.remove('hidden');
    } else {
      notificationBadge.classList.add('hidden');
      notificationBadge.textContent = '';
    }
  }

  function renderNotificationList(items, unreadCount) {
    if (!notificationList) return;
    notificationList.innerHTML = '';
    if (notificationSubtitle) {
      notificationSubtitle.textContent = unreadCount === 1
        ? '1 sin leer'
        : `${unreadCount} sin leer`;
    }

    if (!items.length) {
      const empty = document.createElement('div');
      empty.className = 'px-4 py-8 text-center text-sm text-slate-500';
      empty.textContent = 'No tienes notificaciones.';
      notificationList.appendChild(empty);
      return;
    }

    items.forEach(item => {
      const row = document.createElement('div');
      row.className = `px-4 py-3 ${item.status === 'unread' ? 'bg-emerald-50/30' : 'bg-white'}`;

      const header = document.createElement('div');
      header.className = 'flex items-center gap-2';

      const type = document.createElement('span');
      type.className = `rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase ${notificationTypeClass(item.type)}`;
      type.textContent = item.type || 'info';
      header.appendChild(type);

      if (item.priority === 'high') {
        const priority = document.createElement('span');
        priority.className = 'rounded-full bg-rose-50 px-2 py-0.5 text-[10px] font-semibold uppercase text-rose-700';
        priority.textContent = 'Alta';
        header.appendChild(priority);
      }

      const title = document.createElement('p');
      title.className = 'mt-2 text-sm font-semibold text-slate-900';
      title.textContent = item.title || 'Notificacion';

      const body = document.createElement('p');
      body.className = 'mt-1 line-clamp-2 text-xs text-slate-600';
      body.textContent = item.body || '';

      const footer = document.createElement('div');
      footer.className = 'mt-3 flex items-center justify-between gap-2';

      const linkWrap = document.createElement('div');
      linkWrap.className = 'flex items-center gap-2';

      if (item.link_url) {
        const link = document.createElement('a');
        link.href = item.link_url;
        link.className = 'text-xs font-semibold text-emerald-700 hover:text-emerald-800';
        link.textContent = 'Abrir';
        linkWrap.appendChild(link);
      }

      if (item.status === 'unread') {
        const markRead = document.createElement('button');
        markRead.type = 'button';
        markRead.className = 'text-xs font-semibold text-slate-500 hover:text-slate-700';
        markRead.textContent = 'Leida';
        markRead.addEventListener('click', () => {
          postNotificationAction(endpoint(`/api/${item.id}/read`)).then(loadNotifications);
        });
        linkWrap.appendChild(markRead);
      }

      const date = document.createElement('span');
      date.className = 'text-[11px] text-slate-400';
      date.textContent = item.sent_at ? new Date(item.sent_at).toLocaleDateString() : '';

      footer.appendChild(linkWrap);
      footer.appendChild(date);
      row.appendChild(header);
      row.appendChild(title);
      row.appendChild(body);
      row.appendChild(footer);
      notificationList.appendChild(row);
    });
  }

  function loadNotifications() {
    if (!notificationWrapper) return Promise.resolve();
    return fetch(notificationWrapper.dataset.recentUrl || endpoint('/api/recent'))
      .then(response => response.json())
      .then(data => {
        updateNotificationBadge(data.unread_count || 0);
        renderNotificationList(data.notifications || [], data.unread_count || 0);
      })
      .catch(() => {
        if (notificationSubtitle) notificationSubtitle.textContent = 'No se pudo cargar';
      });
  }

  function showNotificationPopup(item) {
    const modal = document.getElementById('notification-popup-modal');
    if (!modal || !item) return;

    const typeBadge = document.getElementById('notification-popup-type');
    const title = document.getElementById('notification-popup-title');
    const body = document.getElementById('notification-popup-body');
    const ack = document.getElementById('notification-popup-ack');
    const link = document.getElementById('notification-popup-link');

    if (typeBadge) {
      typeBadge.className = `mb-3 inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold uppercase ${notificationTypeClass(item.type)}`;
      typeBadge.textContent = item.type || 'Aviso';
    }
    if (title) title.textContent = item.title || 'Notificacion';
    if (body) body.textContent = item.body || '';
    if (link) {
      if (item.link_url) {
        link.href = item.link_url;
        link.classList.remove('hidden');
      } else {
        link.classList.add('hidden');
      }
    }

    const close = () => {
      postNotificationAction(endpoint(`/api/${item.id}/read`))
        .finally(() => {
          modal.classList.add('hidden');
          document.body.style.overflow = '';
          loadNotifications();
        });
    };

    const nextAck = ack?.cloneNode(true);
    if (ack && nextAck) {
      ack.replaceWith(nextAck);
      nextAck.addEventListener('click', close);
    }

    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  }

  function loadPopupNotifications() {
    if (!notificationWrapper) return;
    fetch(notificationWrapper.dataset.popupsUrl || endpoint('/api/popups'))
      .then(response => response.json())
      .then(data => {
        const items = data.notifications || [];
        if (items.length) showNotificationPopup(items[0]);
      })
      .catch(() => {});
  }

  if (notificationBtn && notificationMenu) {
    notificationBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      notificationMenu.classList.toggle('hidden');
      loadNotifications();
    });

    notificationMenu.addEventListener('click', (e) => e.stopPropagation());

    document.addEventListener('click', () => {
      notificationMenu.classList.add('hidden');
    });

    notificationMarkAllBtn?.addEventListener('click', () => {
      postNotificationAction(notificationWrapper.dataset.markAllUrl || endpoint('/api/mark-all-read'))
        .then(loadNotifications);
    });

    document.querySelectorAll('[data-notification-read]').forEach(button => {
      button.addEventListener('click', () => {
        postNotificationAction(endpoint(`/api/${button.dataset.notificationRead}/read`))
          .then(() => window.location.reload());
      });
    });

    const centerMarkAllBtn = document.getElementById('notifications-mark-all-center');
    centerMarkAllBtn?.addEventListener('click', () => {
      postNotificationAction(notificationWrapper.dataset.markAllUrl || endpoint('/api/mark-all-read'))
        .then(() => window.location.reload());
    });

    loadNotifications();
    loadPopupNotifications();
  }

});
