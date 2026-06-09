(function () {
  const dataElement = document.getElementById('invoice-form-data');
  if (!dataElement) {
    return;
  }

  let formData;
  try {
    formData = JSON.parse(dataElement.textContent);
  } catch (error) {
    console.error('Invoice form data parsing failed:', error);
    return;
  }

  const docType = formData.docType || 'invoice';
  const isInvoice = docType === 'invoice';
  const clients = Array.isArray(formData.clients) ? formData.clients : [];
  const inventoryItems = Array.isArray(formData.inventoryItems) ? formData.inventoryItems : [];
  let itemIndex = Number(formData.itemIndex) || 0;
  let activeProductTargetRow = null;

  const customerModal = document.getElementById('customer-modal');
  const openCustomerModalBtn = document.getElementById('open-client-modal-btn');
  const changeClientBtn = document.getElementById('change-client-btn');
  const closeCustomerModal = document.getElementById('close-customer-modal');
  const customerSearchInput = document.getElementById('customer-search-input');
  const customerListBox = document.getElementById('customer-list-box');

  const clientPlaceholder = document.getElementById('client-selection-placeholder');
  const clientSelectedCard = document.getElementById('client-selected-card');
  const clientHiddenInput = document.getElementById('selected-client-id');

  const clientAvatar = document.getElementById('client-avatar-initials');
  const clientDisplayName = document.getElementById('client-display-name');
  const clientDisplayId = document.getElementById('client-display-identifier');
  const clientDisplayEmail = document.getElementById('client-display-email');

  const productModal = document.getElementById('product-modal');
  const closeProductModal = document.getElementById('close-product-modal');
  const productSearchInput = document.getElementById('product-search-input');
  const productListBox = document.getElementById('product-list-box');

  const projectModal = document.getElementById('project-modal');
  const openProjectModalBtn = document.getElementById('open-project-modal-btn');
  const closeProjectModal = document.getElementById('close-project-modal');
  const projectSearchInput = document.getElementById('project-search-input');
  const projectListBox = document.getElementById('project-list-box');
  const projectHiddenInput = document.getElementById('selected-project-id');
  const projectDisplayName = document.getElementById('project-display-name');
  const clearProjectBtn = document.getElementById('clear-project-btn');

  const projects = Array.isArray(formData.projects) ? formData.projects : [];

  function openCustomerSearch() {
    customerModal?.classList.remove('hidden');
    if (customerSearchInput) {
      customerSearchInput.value = '';
      customerSearchInput.focus();
    }
    renderCustomers('');
  }

  function closeCustomerSearch() {
    customerModal?.classList.add('hidden');
  }

  function renderCustomers(searchQuery) {
    if (!customerListBox) return;

    customerListBox.innerHTML = '';
    const q = searchQuery.toLowerCase();
    const filtered = clients.filter(c => {
      const name = String(c.name || '').toLowerCase();
      const identifier = String(c.identifier || '').toLowerCase();
      return name.includes(q) || identifier.includes(q);
    });

    if (filtered.length === 0) {
      customerListBox.innerHTML = `
        <div class="py-8 text-center text-sm text-slate-400">
          Ningún cliente coincide con la búsqueda
        </div>`;
      return;
    }

    filtered.forEach(c => {
      const div = document.createElement('div');
      div.className = 'flex items-center justify-between p-3 rounded-lg hover:bg-slate-50 cursor-pointer transition-colors';
      div.innerHTML = `
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-full bg-sky-50 border border-sky-100 flex items-center justify-center text-sky-600 text-xs font-bold flex-shrink-0">
            ${String(c.name || '').substring(0, 2).toUpperCase()}
          </div>
          <div>
            <p class="text-sm font-semibold text-slate-800">${c.name || ''}</p>
            <p class="text-xs text-slate-400 mt-0.5">${c.identifier ? 'RTN: ' + c.identifier : 'Sin RTN'}${c.email ? ' · ' + c.email : ''}</p>
          </div>
        </div>
        <svg class="w-5 h-5 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
        </svg>`;

      div.addEventListener('click', () => selectCustomer(c));
      customerListBox.appendChild(div);
    });
  }

  function selectCustomer(client) {
    if (!clientHiddenInput) return;

    clientHiddenInput.value = client.id;
    if (clientDisplayName) clientDisplayName.textContent = client.name || '';
    if (clientDisplayId) clientDisplayId.textContent = client.identifier ? 'RTN / ID: ' + client.identifier : 'Sin Identificador';
    if (clientDisplayEmail) clientDisplayEmail.textContent = client.email || '';
    if (clientAvatar) clientAvatar.textContent = String(client.name || '').substring(0, 2).toUpperCase();

    clientPlaceholder?.classList.add('hidden');
    clientSelectedCard?.classList.remove('hidden');
    closeCustomerSearch();
  }

  function openProductSearch(row) {
    activeProductTargetRow = row;
    productModal?.classList.remove('hidden');
    if (productSearchInput) {
      productSearchInput.value = '';
      productSearchInput.focus();
    }
    renderProducts('');
  }

  function closeProductSearch() {
    productModal?.classList.add('hidden');
    activeProductTargetRow = null;
  }

  function openProjectSearch() {
    projectModal?.classList.remove('hidden');
    if (projectSearchInput) {
      projectSearchInput.value = '';
      projectSearchInput.focus();
    }
    renderProjects('');
  }

  function closeProjectSearch() {
    projectModal?.classList.add('hidden');
  }

  function renderProjects(searchQuery) {
    if (!projectListBox) return;

    projectListBox.innerHTML = '';
    const q = String(searchQuery || '').toLowerCase();
    const filtered = projects.filter(project => {
      const name = String(project.name || '').toLowerCase();
      const description = String(project.description || '').toLowerCase();
      return name.includes(q) || description.includes(q);
    });

    if (filtered.length === 0) {
      projectListBox.innerHTML = `
        <div class="py-8 text-center text-sm text-slate-400">
          Ningún proyecto coincide con la búsqueda
        </div>`;
      return;
    }

    filtered.forEach(project => {
      const div = document.createElement('div');
      div.className = 'p-3 rounded-lg hover:bg-slate-50 cursor-pointer transition-colors border border-transparent hover:border-slate-200';
      div.innerHTML = `
        <div class="flex items-start justify-between gap-3">
          <div>
            <p class="text-sm font-semibold text-slate-800">${project.name || ''}</p>
            <p class="text-xs text-slate-500 mt-1">${project.description || 'Sin descripción'}</p>
          </div>
          <span class="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">${project.status || 'Sin estado'}</span>
        </div>`;

      div.addEventListener('click', () => selectProject(project));
      projectListBox.appendChild(div);
    });
  }

  function selectProject(project) {
    if (!projectHiddenInput) return;

    projectHiddenInput.value = project.id;
    if (projectDisplayName) projectDisplayName.textContent = project.name || '';
    if (projectDisplayName) projectDisplayName.classList.remove('text-slate-400');
    if (clearProjectBtn) clearProjectBtn.classList.remove('hidden');

    closeProjectSearch();
  }

  function clearSelectedProject() {
    if (!projectHiddenInput) return;

    projectHiddenInput.value = '';
    if (projectDisplayName) {
      projectDisplayName.textContent = 'Sin proyecto asignado...';
      projectDisplayName.classList.add('text-slate-400');
    }
    if (clearProjectBtn) clearProjectBtn.classList.add('hidden');
  }

  function renderProducts(searchQuery) {
    if (!productListBox) return;

    productListBox.innerHTML = '';
    const q = String(searchQuery || '').toLowerCase();
    const filtered = inventoryItems.filter(p => String(p.name || '').toLowerCase().includes(q));

    if (filtered.length === 0) {
      productListBox.innerHTML = `
        <div class="py-8 text-center text-sm text-slate-400">
          Ningún producto coincide con la búsqueda
        </div>`;
      return;
    }

    filtered.forEach(p => {
      const stockVal = Number(p.stock) || 0;
      const isOutOfStock = stockVal <= 0;
      const isBlocked = isInvoice && isOutOfStock;

      const div = document.createElement('div');
      div.className = `flex items-center justify-between p-3 rounded-lg hover:bg-slate-50 cursor-pointer transition-colors ${isBlocked ? 'opacity-50 cursor-not-allowed' : ''}`;

      const badgeHtml = isOutOfStock
        ? `<span class="text-[10px] font-bold text-rose-700 bg-rose-50 border border-rose-100 rounded px-2 py-0.5">Sin Stock${isBlocked ? ' (Bloqueado)' : ''}</span>`
        : `<span class="text-[10px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-100 rounded px-2 py-0.5">${stockVal} unids</span>`;

      div.innerHTML = `
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-lg bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-600 text-xs font-bold flex-shrink-0">
            PR
          </div>
          <div>
            <div class="flex items-center gap-2">
              <p class="text-sm font-semibold text-slate-800">${p.name || ''}</p>
              ${badgeHtml}
            </div>
            <p class="text-xs text-slate-400 mt-0.5">${p.price ? 'Precio base: ' + Number(p.price).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : 'Sin precio configurado'}</p>
          </div>
        </div>
        <span class="text-sm font-bold text-slate-700 px-2.5 py-1 rounded bg-slate-100">${Number(p.price).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>`;

      if (!isBlocked) {
        div.addEventListener('click', () => selectProduct(p));
      }

      productListBox.appendChild(div);
    });
  }

  function selectProduct(product) {
    if (!activeProductTargetRow) return;

    const row = activeProductTargetRow;
    const idInput = row.querySelector('.item-product-id');
    const nameInput = row.querySelector('.item-product-trigger');
    const descInput = row.querySelector('input[name*="[description]"]');
    const priceInput = row.querySelector('.item-price');
    const clearBtn = row.querySelector('.clear-product-btn');

    if (idInput) idInput.value = product.id;
    if (nameInput) nameInput.value = product.name || '';
    if (descInput && !descInput.value) descInput.value = product.name || '';
    if (priceInput) priceInput.value = Number(product.price).toFixed(2);
    if (clearBtn) clearBtn.classList.remove('hidden');

    updateTotals();
    closeProductSearch();
  }

  function buildItemRowMarkup(idx) {
    return `
      <tr class="item-row hover:bg-slate-50/30 transition-colors">
        <td class="px-4 py-3">
          <input type="hidden" name="items[${idx}][inventory_item_id]" class="item-product-id" value="">
          <div class="relative flex items-center">
            <input type="text" readonly placeholder="Buscar en catálogo..."
                   class="item-product-trigger w-full pl-3 pr-8 py-1.5 border border-slate-200 rounded-lg text-sm bg-slate-50 cursor-pointer focus:outline-none hover:bg-slate-100 transition-colors font-medium text-slate-700">
            <button type="button" class="clear-product-btn absolute right-2 text-slate-400 hover:text-rose-500 hidden" title="Remover producto catálogo">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
        </td>
        <td class="px-4 py-3">
          <input type="text" name="items[${idx}][description]" placeholder="Escriba descripción..."
                 class="w-full text-sm border border-slate-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-emerald-500 bg-white text-slate-700">
        </td>
        <td class="px-4 py-3">
          <input type="number" name="items[${idx}][quantity]" value="1" min="1" step="1"
                 class="w-full text-sm border border-slate-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-emerald-500 text-right item-qty font-medium text-slate-700">
        </td>
        <td class="px-4 py-3">
          <input type="number" name="items[${idx}][unit_price]" value="0.00" min="0" step="0.01"
                 class="w-full text-sm border border-slate-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-emerald-500 text-right item-price font-medium text-slate-700">
        </td>
        <td class="px-4 py-3">
          <input type="number" name="items[${idx}][discount]" value="0" min="0" max="100" step="0.1"
                 class="w-full text-sm border border-slate-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-emerald-500 text-right item-discount font-semibold text-rose-600 bg-rose-50/20">
        </td>
        <td class="px-4 py-3 text-sm font-bold text-slate-800 text-right item-subtotal">0.00</td>
        <td class="px-2 py-3 text-center">
          <button type="button" class="remove-item text-slate-400 hover:text-rose-500 transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
            </svg>
          </button>
        </td>
      </tr>`;
  }

  function updateTotals() {
    let subtotal = 0;
    document.querySelectorAll('#items-body .item-row').forEach(row => {
      const qty = Number(row.querySelector('.item-qty')?.value) || 0;
      const price = Number(row.querySelector('.item-price')?.value) || 0;
      const discount = Number(row.querySelector('.item-discount')?.value) || 0;
      const sub = qty * price * (1 - discount / 100);
      const subtotalCell = row.querySelector('.item-subtotal');
      if (subtotalCell) subtotalCell.textContent = sub.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
      subtotal += sub;
    });

    const generalDiscount = Number(document.getElementById('discount-input')?.value) || 0;
    const total = Math.max(0, subtotal - generalDiscount);

    const subtotalDisplay = document.getElementById('subtotal-display');
    const totalDisplay = document.getElementById('total-display');
    const sidebarTotalDisplay = document.getElementById('sidebar-total-display');
    if (subtotalDisplay) subtotalDisplay.textContent = subtotal.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (totalDisplay) totalDisplay.textContent = total.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (sidebarTotalDisplay) sidebarTotalDisplay.textContent = total.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function bindRowEvents(row) {
    row.querySelector('.remove-item')?.addEventListener('click', () => {
      row.remove();
      updateTotals();
    });

    row.querySelector('.item-qty')?.addEventListener('input', updateTotals);
    row.querySelector('.item-price')?.addEventListener('input', updateTotals);
    row.querySelector('.item-discount')?.addEventListener('input', updateTotals);
    row.querySelector('.item-product-trigger')?.addEventListener('click', () => openProductSearch(row));
    row.querySelector('.clear-product-btn')?.addEventListener('click', function (e) {
      e.stopPropagation();
      row.querySelector('.item-product-id').value = '';
      const productTrigger = row.querySelector('.item-product-trigger');
      if (productTrigger) productTrigger.value = 'Servicio Manual';
      this.classList.add('hidden');
      updateTotals();
    });
  }

  if (openCustomerModalBtn) openCustomerModalBtn.addEventListener('click', openCustomerSearch);
  if (changeClientBtn) changeClientBtn.addEventListener('click', openCustomerSearch);
  if (closeCustomerModal) closeCustomerModal.addEventListener('click', closeCustomerSearch);
  if (customerSearchInput) customerSearchInput.addEventListener('input', () => renderCustomers(customerSearchInput.value));
  if (closeProductModal) closeProductModal.addEventListener('click', closeProductSearch);
  if (productSearchInput) productSearchInput.addEventListener('input', () => renderProducts(productSearchInput.value));

  if (openProjectModalBtn) openProjectModalBtn.addEventListener('click', openProjectSearch);
  if (closeProjectModal) closeProjectModal.addEventListener('click', closeProjectSearch);
  if (projectSearchInput) projectSearchInput.addEventListener('input', () => renderProjects(projectSearchInput.value));
  if (clearProjectBtn) clearProjectBtn.addEventListener('click', (event) => {
    event.stopPropagation();
    clearSelectedProject();
  });

  document.getElementById('add-item-btn')?.addEventListener('click', () => {
    const temp = document.createElement('tbody');
    temp.innerHTML = buildItemRowMarkup(itemIndex++);
    const newRow = temp.firstElementChild;
    if (!newRow) return;
    document.getElementById('items-body')?.appendChild(newRow);
    bindRowEvents(newRow);
    updateTotals();
  });

  document.querySelectorAll('#items-body .item-row').forEach(bindRowEvents);
  document.getElementById('discount-input')?.addEventListener('input', updateTotals);
  updateTotals();
})();
