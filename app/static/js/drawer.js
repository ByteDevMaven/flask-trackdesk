/**
 * drawer.js - Controlador de paneles laterales (drawers) con carga AJAX.
 * NO contiene referencias a Jinja ni variables de plantilla.
 * Los datos dinámicos se leen desde atributos data-* en el HTML.
 */

'use strict';


function openDrawer(title) {
  const drawer = document.getElementById('side-drawer');
  const overlay = document.getElementById('drawer-overlay');
  const titleEl = document.getElementById('drawer-title');
  if (!drawer || !overlay) return;

  if (titleEl) titleEl.textContent = title || 'Formulario';

  overlay.classList.remove('hidden');
  drawer.classList.remove('translate-x-full');
  document.body.style.overflow = 'hidden';
}

function closeDrawer() {
  const drawer = document.getElementById('side-drawer');
  const overlay = document.getElementById('drawer-overlay');
  if (!drawer || !overlay) return;

  drawer.classList.add('translate-x-full');
  overlay.classList.add('hidden');
  document.body.style.overflow = '';

  setTimeout(() => {
    const body = document.getElementById('drawer-body');
    if (body) body.replaceChildren();
  }, 300);
}

window.closeDrawer = closeDrawer;


async function loadDrawerContent(url, title) {
  const body = document.getElementById('drawer-body');
  if (!body) return;

  // Clear body safely
  body.replaceChildren();

  // Create loading element safely using document.createElement
  const loaderWrapper = document.createElement('div');
  loaderWrapper.className = 'flex items-center justify-center h-64';
  const loader = document.createElement('div');
  loader.className = 'w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin';
  loaderWrapper.appendChild(loader);
  body.appendChild(loaderWrapper);

  openDrawer(title);

  try {
    const res = await fetch(url, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const html = await res.text();
    
    // Parse fetched HTML string safely using DOMParser
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    
    // Clear spinner and append parsed HTML nodes safely
    body.replaceChildren();
    while (doc.body.firstChild) {
      body.appendChild(doc.body.firstChild);
    }

    // Evaluate injected scripts so form-specific JS (like receipt previews) runs perfectly
    body.querySelectorAll('script').forEach(script => {
      const newScript = document.createElement('script');
      if (script.src) {
        newScript.src = script.src;
      } else {
        newScript.textContent = script.textContent;
      }
      document.body.appendChild(newScript);
      newScript.remove();
    });

    const form = body.querySelector('form[data-drawer-form]');
    if (form) attachDrawerFormSubmit(form);

  } catch (err) {
    // Clear body safely
    body.replaceChildren();
    
    // Parse static error HTML template safely using DOMParser
    const errorParser = new DOMParser();
    const errorDoc = errorParser.parseFromString(`
      <div class="p-6 text-center">
        <div class="w-12 h-12 bg-rose-100 rounded-full flex items-center justify-center mx-auto mb-3">
          <svg class="w-6 h-6 text-rose-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </div>
        <p class="text-sm text-slate-600">Error al cargar el formulario</p>
        <button id="drawer-error-close-btn" class="mt-3 text-sm text-emerald-600 hover:text-emerald-700 font-medium">Cerrar</button>
      </div>
    `, 'text/html');
    
    while (errorDoc.body.firstChild) {
      body.appendChild(errorDoc.body.firstChild);
    }
    
    const errBtn = body.querySelector('#drawer-error-close-btn');
    if (errBtn) {
      errBtn.addEventListener('click', closeDrawer);
    }
  }
}

function attachDrawerFormSubmit(form) {
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const submitBtn = form.querySelector('[type="submit"]');
    const originalText = submitBtn?.textContent || 'Guardar';
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Guardando...';
    }

    form.querySelectorAll('.field-error').forEach(el => el.remove());
    form.querySelectorAll('.border-rose-500').forEach(el => {
      el.classList.remove('border-rose-500');
    });

    try {
      const formData = new FormData(form);
      const res = await fetch(form.action, {
        method: form.method || 'POST',
        body: formData,
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      });

      const data = await res.json().catch(() => null);

      if (res.ok && (!data || data.success !== false)) {
        closeDrawer();

        const successMsg = form.dataset.successMessage || 'Operación exitosa';
        window.triggerToast(successMsg, true);

        const reloadTarget = form.dataset.reloadTarget;
        if (reloadTarget) {
          const target = document.querySelector(reloadTarget);
          if (target) {
            await reloadSection(target);
          }
        } else {
          setTimeout(() => location.reload(), 600);
        }

      } else {
        if (data && data.errors) {
          Object.entries(data.errors).forEach(([field, msg]) => {
            const input = form.querySelector(`[name="${field}"]`);
            if (input) {
              input.classList.add('border-rose-500');
              const errorEl = document.createElement('p');
              errorEl.className = 'field-error text-xs text-rose-600 mt-1';
              errorEl.textContent = msg;
              input.parentNode.appendChild(errorEl);
            }
          });
        }

        const errorMsg = (data && data.message) || 'Error al guardar. Verifique los datos.';
        window.triggerToast(errorMsg, false);

        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = originalText;
        }
      }

    } catch (err) {
      window.triggerToast('Error de conexión. Intente nuevamente.', false);
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
      }
    }
  });
}

async function reloadSection(target) {
  try {
    const url = target.dataset.reloadUrl || location.href;
    const res = await fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
    const html = await res.text();
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const newContent = doc.querySelector(target.id ? `#${target.id}` : target.className);
    if (newContent) {
      target.replaceChildren();
      while (newContent.firstChild) {
        target.appendChild(newContent.firstChild);
      }
    }
  } catch {
    location.reload();
  }
}


document.addEventListener('DOMContentLoaded', () => {
  const overlay = document.getElementById('drawer-overlay');
  const closeBtn = document.getElementById('drawer-close-btn');

  if (overlay) overlay.addEventListener('click', closeDrawer);
  if (closeBtn) closeBtn.addEventListener('click', closeDrawer);

  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-action="open-drawer"]');
    if (!btn) return;

    e.preventDefault();
    const url = btn.dataset.url;
    const title = btn.dataset.title || 'Formulario';
    if (url) loadDrawerContent(url, title);
  });

  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-action="confirm-delete"]');
    if (!btn) return;

    e.preventDefault();
    const name = btn.dataset.name || 'este elemento';
    const url = btn.dataset.url;

    window.showConfirmModal({
      title: 'Eliminar registro',
      message: `¿Estás seguro de eliminar "${name}"? Esta acción no se puede deshacer.`,
      confirmText: 'Eliminar',
      cancelText: 'Cancelar',
      type: 'danger',
      onConfirm: () => {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = url;

        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrf_token';
        const meta = document.querySelector('meta[name="csrf-token"]');
        csrfInput.value = meta ? meta.content : '';
        form.appendChild(csrfInput);

        document.body.appendChild(form);
        form.submit();
      }
    });
  });
});
