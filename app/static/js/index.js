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

});