/**
 * modals.js - Controlador global de modales y notificaciones toast.
 * NO contiene referencias a Jinja ni variables de plantilla.
 * Todos los datos dinámicos se reciben mediante parámetros de función o data-attributes.
 */

'use strict';

// ─── Toast Notifications ─────────────────────────────────────────────────────

/**
 * Muestra una notificación toast deslizante.
 * @param {string} message - Mensaje a mostrar
 * @param {boolean} isSuccess - true = éxito (verde), false = error (rojo)
 * @param {number} duration - Duración en ms antes de desaparecer (default 4000)
 */
window.triggerToast = function(message, isSuccess = true, duration = 4000) {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  const colorClasses = isSuccess
    ? 'bg-white border-emerald-500 text-emerald-700'
    : 'bg-white border-rose-500 text-rose-700';

  const iconPath = isSuccess
    ? 'M5 13l4 4L19 7'
    : 'M6 18L18 6M6 6l12 12';

  const iconColor = isSuccess ? 'text-emerald-500' : 'text-rose-500';

  toast.className = [
    'flex items-center gap-3 px-4 py-3 rounded-lg border-l-4 shadow-lg',
    'bg-white text-sm font-medium transition-all duration-300 translate-x-full opacity-0',
    colorClasses
  ].join(' ');

  toast.innerHTML = `
    <svg class="w-5 h-5 flex-shrink-0 ${iconColor}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${iconPath}"/>
    </svg>
    <span class="flex-1 text-slate-700">${message}</span>
    <button class="text-slate-400 hover:text-slate-600 transition-colors flex-shrink-0" onclick="this.closest('[class*=toast]').remove()">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
      </svg>
    </button>
  `;

  container.appendChild(toast);

  // Animar entrada
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      toast.classList.remove('translate-x-full', 'opacity-0');
    });
  });

  // Auto-remover
  const timer = setTimeout(() => {
    toast.classList.add('translate-x-full', 'opacity-0');
    setTimeout(() => toast.remove(), 300);
  }, duration);

  // Cancelar al hacer hover
  toast.addEventListener('mouseenter', () => clearTimeout(timer));
};

// ─── Confirm Modal ────────────────────────────────────────────────────────────

/**
 * Muestra un modal de confirmación personalizado.
 * @param {Object} options
 * @param {string} options.title - Título del modal
 * @param {string} options.message - Mensaje descriptivo
 * @param {string} options.confirmText - Texto del botón confirmar (default "Confirmar")
 * @param {string} options.cancelText - Texto del botón cancelar (default "Cancelar")
 * @param {string} options.type - Tipo: 'danger' | 'warning' | 'success' (default 'warning')
 * @param {Function} options.onConfirm - Callback al confirmar
 * @param {Function} [options.onCancel] - Callback al cancelar (opcional)
 */
window.showConfirmModal = function(options) {
  const {
    title = 'Confirmar acción',
    message = '¿Estás seguro de continuar?',
    confirmText = 'Confirmar',
    cancelText = 'Cancelar',
    type = 'warning',
    onConfirm,
    onCancel
  } = options;

  const colorMap = {
    danger:  { icon: 'bg-rose-100',   iconStroke: 'text-rose-600',   btn: 'bg-rose-600 hover:bg-rose-700',   path: 'M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16' },
    warning: { icon: 'bg-amber-100',  iconStroke: 'text-amber-600',  btn: 'bg-emerald-600 hover:bg-emerald-700', path: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z' },
    success: { icon: 'bg-emerald-100', iconStroke: 'text-emerald-600', btn: 'bg-emerald-600 hover:bg-emerald-700', path: 'M5 13l4 4L19 7' },
  };

  const colors = colorMap[type] || colorMap.warning;

  const modal = document.getElementById('confirm-modal');
  if (!modal) return;

  modal.querySelector('#confirm-modal-title').textContent = title;
  modal.querySelector('#confirm-modal-message').textContent = message;
  modal.querySelector('#confirm-modal-icon').className = `w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 ${colors.icon}`;
  modal.querySelector('#confirm-modal-icon svg').setAttribute('class', `w-6 h-6 ${colors.iconStroke}`);
  modal.querySelector('#confirm-modal-icon svg path').setAttribute('d', colors.path);
  modal.querySelector('#confirm-modal-confirm-btn').textContent = confirmText;
  modal.querySelector('#confirm-modal-confirm-btn').className = `flex-1 px-4 py-2 rounded-lg text-sm font-medium text-white transition-colors ${colors.btn}`;
  modal.querySelector('#confirm-modal-cancel-btn').textContent = cancelText;

  modal.classList.remove('hidden');
  document.body.style.overflow = 'hidden';

  const confirmBtn = modal.querySelector('#confirm-modal-confirm-btn');
  const cancelBtn = modal.querySelector('#confirm-modal-cancel-btn');

  const newConfirm = confirmBtn.cloneNode(true);
  const newCancel = cancelBtn.cloneNode(true);
  confirmBtn.replaceWith(newConfirm);
  cancelBtn.replaceWith(newCancel);

  newConfirm.addEventListener('click', () => {
    closeConfirmModal();
    if (typeof onConfirm === 'function') onConfirm();
  });

  newCancel.addEventListener('click', () => {
    closeConfirmModal();
    if (typeof onCancel === 'function') onCancel();
  });
};

function closeConfirmModal() {
  const modal = document.getElementById('confirm-modal');
  if (modal) {
    modal.classList.add('hidden');
    document.body.style.overflow = '';
  }
}

// Cerrar al hacer clic en el backdrop
document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('confirm-modal');
  if (modal) {
    modal.querySelector('#confirm-modal-backdrop').addEventListener('click', closeConfirmModal);
  }

  // Inicializar toasts desde flashes del servidor (renderizados en el DOM)
  document.querySelectorAll('[data-flash-message]').forEach(el => {
    const msg = el.dataset.flashMessage;
    const cat = el.dataset.flashCategory;
    const isSuccess = cat === 'success' || cat === 'info';
    if (msg) window.triggerToast(msg, isSuccess);
    el.remove();
  });
});
