(function () {
  const configEl = document.getElementById("pos-data");
  const config = configEl ? JSON.parse(configEl.textContent || "{}") : {};
  const products = Array.isArray(config.products) ? config.products : [];
  const customers = Array.isArray(config.customers) ? config.customers : [];
  const completedReceipt = config.receipt || null;
  const registerState = config.register || { isOpen: false };
  const currency = String(config.currency || "USD").trim();
  const taxRate = Number(config.taxRate || 0);
  const locale = "es-HN";

  const state = {
    cart: new Map(),
    client: null,
    paymentMethod: "cash",
    amountTouched: false
  };

  const decimalMoney = new Intl.NumberFormat(locale, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });

  let currencyMoney = null;
  if (/^[A-Za-z]{3}$/.test(currency)) {
    try {
      currencyMoney = new Intl.NumberFormat(locale, {
        style: "currency",
        currency: currency.toUpperCase(),
        minimumFractionDigits: 2
      });
    } catch (error) {
      currencyMoney = null;
    }
  }

  const money = {
    format(value) {
      if (currencyMoney) {
        return currencyMoney.format(value);
      }
      return `${currency || "USD"} ${decimalMoney.format(value)}`;
    }
  };

  const $ = (id) => document.getElementById(id);
  const productGrid = $("productGrid");
  const productSearch = $("productSearch");
  const productCount = $("productCount");
  const cartList = $("cartList");
  const subtotalText = $("subtotalText");
  const taxText = $("taxText");
  const totalText = $("totalText");
  const payTotalText = $("payTotalText");
  const receivedText = $("receivedText");
  const changeText = $("changeText");
  const amountReceived = $("amountReceived");
  const cartPayload = $("cartPayload");
  const checkoutForm = $("checkoutForm");
  const paymentMethodInput = $("paymentMethodInput");
  const warehouseSelect = $("warehouseSelect");
  const warehouseInput = $("warehouseInput");
  const terminalFields = $("terminalFields");
  const receiptContent = $("receiptContent");
  const drawerTime = $("drawerTime");
  const methodGrid = $("methodGrid");
  const clientSearch = $("clientSearch");
  const clientResults = $("clientResults");
  const clientIdInput = $("clientIdInput");
  const clientSelectedText = $("clientSelectedText");
  const movementTypeInput = $("movementTypeInput");
  const movementModalTitle = $("movementModalTitle");
  const checkoutBtn = $("checkoutBtn");
  const drawerRegisterName = $("drawerRegisterName");
  const drawerCashierName = $("drawerCashierName");
  let pendingDrawerPrint = false;

  function formatAmount(value) {
    return money.format(Number(value || 0));
  }

  function formatPlain(value) {
    return Number(value || 0).toFixed(2);
  }

  function formatReceiptAmount(value) {
    const label = currencyMoney ? currency.toUpperCase() : currency || "USD";
    return `${label} ${formatPlain(value)}`;
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function calcTotals() {
    let subtotal = 0;
    state.cart.forEach((item) => {
      subtotal += item.quantity * item.unit_price * (1 - item.discount / 100);
    });
    const tax = subtotal * (taxRate / 100);
    const total = subtotal + tax;
    return { subtotal, tax, total };
  }

  function syncAmountDefault() {
    if (state.amountTouched) {
      return;
    }
    const totals = calcTotals();
    amountReceived.value = totals.total.toFixed(2);
  }

  function renderRegisterSummary() {
    const cashIn = Number(registerState.cashIn || 0);
    const cashOut = Number(registerState.cashOut || 0);
    $("openingAmountText").textContent = formatAmount(registerState.openingAmount || 0);
    $("cashSalesText").textContent = formatAmount(registerState.cashSales || 0);
    $("cashMovementText").textContent = formatAmount(cashIn - cashOut);
    $("expectedCashText").textContent = formatAmount(registerState.expectedCash || 0);
    if ($("closeExpectedText")) {
      $("closeExpectedText").textContent = formatAmount(registerState.expectedCash || 0);
    }
    if ($("closeTransactionsText")) {
      $("closeTransactionsText").textContent = String(registerState.transactions || 0);
    }
  }

  function customerLabel(customer) {
    const details = [customer.identifier, customer.phone, customer.email].filter(Boolean).join(" / ");
    return details ? `${customer.name} (${details})` : customer.name;
  }

  function renderClientResults(matches) {
    clientResults.innerHTML = "";
    if (!matches.length) {
      clientResults.innerHTML = '<button class="client-result" type="button" data-client-empty="true"><strong>Consumidor final</strong><span>Sin cliente seleccionado</span></button>';
    } else {
      matches.slice(0, 12).forEach((customer) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "client-result";
        button.dataset.clientId = customer.id;
        button.innerHTML = `
          <strong>${escapeHtml(customer.name)}</strong>
          <span>${escapeHtml([customer.identifier, customer.phone, customer.email].filter(Boolean).join(" / ") || "Sin datos adicionales")}</span>
        `;
        clientResults.appendChild(button);
      });
    }
    clientResults.classList.add("is-open");
  }

  function filterClients() {
    const term = clientSearch.value.trim().toLowerCase();
    if (!term) {
      renderClientResults(customers.slice(0, 8));
      return;
    }

    const matches = customers.filter((customer) => {
      const haystack = `${customer.name} ${customer.identifier} ${customer.phone} ${customer.email}`.toLowerCase();
      return haystack.includes(term);
    });
    renderClientResults(matches);
  }

  function selectClient(customer) {
    state.client = customer || null;
    clientIdInput.value = customer ? customer.id : "";
    clientSearch.value = customer ? customer.name : "";
    clientSelectedText.innerHTML = customer
      ? `<strong>${escapeHtml(customerLabel(customer))}</strong>`
      : "Consumidor final";
    clientResults.classList.remove("is-open");
    renderReceipt();
  }

  function renderProducts(visibleProducts) {
    productGrid.innerHTML = "";
    productCount.textContent = `${visibleProducts.length} disponibles`;

    if (!visibleProducts.length) {
      productGrid.innerHTML = '<div class="empty">No hay productos disponibles.</div>';
      return;
    }

    visibleProducts.forEach((product) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "product-button";
      button.dataset.productId = product.id;
      button.innerHTML = `
        <span class="sku">${product.sku || "Sin SKU"}</span>
        <span class="product-name">${escapeHtml(product.name)}</span>
        <span class="product-meta">
          <span class="price">${formatAmount(product.price)}</span>
          <span>Stock ${product.stock}</span>
        </span>
      `;
      button.addEventListener("click", () => addProduct(product));
      productGrid.appendChild(button);
    });
  }

  function renderCart() {
    cartList.innerHTML = "";

    if (!state.cart.size) {
      cartList.innerHTML = '<div class="empty">Carrito vacio.</div>';
    } else {
      state.cart.forEach((item) => {
        const line = document.createElement("div");
        line.className = "cart-item";
        line.innerHTML = `
          <div>
            <p class="cart-name">${escapeHtml(item.name)}</p>
            <p class="cart-sub">${formatAmount(item.unit_price)} / Desc. ${item.discount}% / Stock ${item.stock}</p>
            <p class="cart-sub"><strong>${formatAmount(item.quantity * item.unit_price * (1 - item.discount / 100))}</strong></p>
          </div>
          <div class="cart-actions">
            <button class="qty-btn" type="button" aria-label="Restar" data-action="minus">-</button>
            <input class="qty-input" type="number" min="1" max="${item.stock}" value="${item.quantity}" aria-label="Cantidad">
            <button class="qty-btn" type="button" aria-label="Sumar" data-action="plus">+</button>
            <button class="remove-line" type="button" data-action="remove">Quitar</button>
          </div>
        `;
        line.querySelector('[data-action="minus"]').addEventListener("click", () => setQuantity(item.id, item.quantity - 1));
        line.querySelector('[data-action="plus"]').addEventListener("click", () => setQuantity(item.id, item.quantity + 1));
        line.querySelector('[data-action="remove"]').addEventListener("click", () => removeProduct(item.id));
        line.querySelector(".qty-input").addEventListener("change", (event) => setQuantity(item.id, Number(event.target.value)));
        cartList.appendChild(line);
      });
    }

    const totals = calcTotals();
    subtotalText.textContent = formatAmount(totals.subtotal);
    taxText.textContent = formatAmount(totals.tax);
    totalText.textContent = formatAmount(totals.total);
    payTotalText.textContent = formatAmount(totals.total);
    syncAmountDefault();
    updatePaymentSummary();
    renderReceipt();
  }

  function addProduct(product) {
    const existing = state.cart.get(product.id);
    const nextQuantity = existing ? existing.quantity + 1 : 1;
    if (nextQuantity > product.stock) {
      showLocalFlash(`Stock insuficiente para ${product.name}.`, "error");
      return;
    }

    state.cart.set(product.id, {
      id: product.id,
      sku: product.sku,
      name: product.name,
      description: product.description || product.name,
      quantity: nextQuantity,
      unit_price: Number(product.price || 0),
      discount: Number(product.discount || 0),
      stock: Number(product.stock || 0)
    });
    renderCart();
  }

  function setQuantity(productId, quantity) {
    const item = state.cart.get(productId);
    if (!item) {
      return;
    }
    const next = Math.max(1, Math.min(Number(quantity || 1), item.stock));
    item.quantity = next;
    state.cart.set(productId, item);
    renderCart();
  }

  function removeProduct(productId) {
    state.cart.delete(productId);
    renderCart();
  }

  function clearCart() {
    state.cart.clear();
    state.amountTouched = false;
    amountReceived.value = "0.00";
    renderCart();
  }

  function updatePaymentSummary() {
    const totals = calcTotals();
    const received = Number(amountReceived.value || 0);
    const change = Math.max(received - totals.total, 0);
    receivedText.textContent = formatAmount(received);
    changeText.textContent = formatAmount(change);
  }

  function filterProducts() {
    const term = productSearch.value.trim().toLowerCase();
    if (!term) {
      renderProducts(products);
      return products;
    }

    const filtered = products.filter((product) => {
      const haystack = `${product.sku} ${product.name} ${product.description}`.toLowerCase();
      return haystack.includes(term);
    });
    renderProducts(filtered);
    return filtered;
  }

  function setPaymentMethod(method) {
    state.paymentMethod = method;
    paymentMethodInput.value = method;
    document.querySelectorAll(".method-button").forEach((button) => {
      button.classList.toggle("active", button.dataset.method === method);
    });
    terminalFields.classList.toggle("is-hidden", method === "cash");
  }

  function renderReceipt() {
    const source = completedReceipt || liveReceipt();
    if (!source) {
      receiptContent.innerHTML = "";
      return;
    }

    const sequence = source.sequence || config.sequence || {};
    const paidAmount = Number(source.paid || amountReceived.value || 0);
    const changeAmount = Math.max(paidAmount - Number(source.total || 0), 0);
    const issuedDateTime = [source.issued_date, source.issued_time].filter(Boolean).join(" ");
    const taxBase = Math.max(Number(source.subtotal || 0), 0);
    const taxLabel = formatPlain(taxRate).replace(/\.00$/, "");
    const lines = source.lines.map((line) => `
      <div class="receipt-item">
        <div class="receipt-item-name">${escapeHtml(line.description)}</div>
        <div class="receipt-row receipt-item-calc">
          <span>${line.quantity} x ${formatReceiptAmount(line.unit_price)}</span>
          <span>${formatReceiptAmount(line.line_total)}</span>
        </div>
      </div>
    `).join("");

    receiptContent.innerHTML = `
      <div class="receipt-title">Factura</div>
      <div class="receipt-sar">
        <div>No. ${escapeHtml(source.number || "POS")}</div>
        ${sequence.cai ? `<div>CAI: ${escapeHtml(sequence.cai)}</div>` : ""}
        ${sequence.range_label ? `<div>Rango Autorizado SAR:<br>${escapeHtml(sequence.range_label)}</div>` : ""}
        ${sequence.expiration_date ? `<div>Fecha Limite Emision: ${escapeHtml(sequence.expiration_date)}</div>` : ""}
        <div>Fecha/Hora: ${escapeHtml(issuedDateTime || new Date().toLocaleString(locale))}</div>
        <div>Cajero: ${escapeHtml(config.cashierName || "")}</div>
      </div>
      <div class="receipt-rule"></div>
      <div class="receipt-customer">
        Cliente: ${escapeHtml(source.client_name || "Consumidor final")}<br>
        RTN/Identidad: ${escapeHtml(source.client_identifier || "Consumidor final")}
      </div>
      <div class="receipt-rule"></div>
      <div class="receipt-items">${lines}</div>
      <div class="receipt-rule"></div>
      <div class="receipt-totals">
        <div class="receipt-row"><span>Importe Exento</span><span>${formatReceiptAmount(0)}</span></div>
        <div class="receipt-row"><span>Importe Exonerado</span><span>${formatReceiptAmount(0)}</span></div>
        <div class="receipt-row"><span>Importe Gravado ${taxLabel}%</span><span>${formatReceiptAmount(taxBase)}</span></div>
        <div class="receipt-row"><span>ISV ${taxLabel}%</span><span>${formatReceiptAmount(source.tax)}</span></div>
        <div class="receipt-row"><span>Subtotal</span><span>${formatReceiptAmount(source.subtotal)}</span></div>
        <div class="receipt-row receipt-total"><span>Total</span><span>${formatReceiptAmount(source.total)}</span></div>
        <div class="receipt-row"><span>Pagado</span><span>${formatReceiptAmount(paidAmount)}</span></div>
        <div class="receipt-row"><span>Cambio</span><span>${formatReceiptAmount(changeAmount)}</span></div>
      </div>
      <div class="receipt-legal">
        Original: Cliente / Copia: Emisor<br>
        La factura es beneficio de todos. Exijala.
      </div>
    `;
  }

  function liveReceipt() {
    const totals = calcTotals();
    if (!state.cart.size) {
      return null;
    }
    return {
      number: "POS",
      issued_date: new Date().toISOString().slice(0, 10),
      issued_time: new Date().toLocaleTimeString(locale, { hour: "2-digit", minute: "2-digit" }),
      client_name: state.client?.name || "Consumidor final",
      client_identifier: state.client?.identifier || "",
      subtotal: totals.subtotal,
      tax: totals.tax,
      total: totals.total,
      paid: Number(amountReceived.value || 0),
      sequence: config.sequence || {},
      lines: Array.from(state.cart.values()).map((item) => ({
        description: item.description,
        quantity: item.quantity,
        unit_price: item.unit_price,
        line_total: item.quantity * item.unit_price * (1 - item.discount / 100)
      }))
    };
  }

  function prepareCheckout(event) {
    if (!registerState.isOpen) {
      event.preventDefault();
      showLocalFlash("Debe abrir caja antes de cobrar.", "error");
      return;
    }

    if (!state.cart.size) {
      event.preventDefault();
      showLocalFlash("Agrega al menos un producto antes de cobrar.", "error");
      return;
    }

    const totals = calcTotals();
    const received = Number(amountReceived.value || 0);
    if (received < 0 || Number.isNaN(received)) {
      event.preventDefault();
      showLocalFlash("El monto recibido no es valido.", "error");
      return;
    }
    if (state.paymentMethod !== "cash" && received > 0 && Math.abs(received - totals.total) > 0.01) {
      amountReceived.value = totals.total.toFixed(2);
    }

    cartPayload.value = JSON.stringify(Array.from(state.cart.values()).map((item) => ({
      id: item.id,
      description: item.description,
      quantity: item.quantity,
      unit_price: item.unit_price,
      discount: item.discount
    })));
  }

  function printReceipt(mode = "sale") {
    document.body.dataset.printMode = mode;
    if (mode === "drawer") {
      drawerTime.textContent = new Date().toLocaleString(locale);
      if (drawerRegisterName) {
        drawerRegisterName.textContent = registerState.registerName || "Caja POS";
      }
      if (drawerCashierName) {
        drawerCashierName.textContent = config.cashierName || "";
      }
      pendingDrawerPrint = true;
    } else {
      renderReceipt();
    }
    window.print();
    window.setTimeout(() => {
      document.body.dataset.printMode = "";
    }, 400);
  }

  function openDrawer() {
    if (!registerState.isOpen) {
      showLocalFlash("Debe abrir caja antes de usar la gaveta.", "error");
      return;
    }
    printReceipt("drawer");
  }

  function showLocalFlash(message, category) {
    let stack = document.querySelector(".flash-stack");
    if (!stack) {
      stack = document.createElement("div");
      stack.className = "flash-stack";
      document.body.appendChild(stack);
    }
    const el = document.createElement("div");
    el.className = `flash ${category}`;
    el.textContent = message;
    stack.appendChild(el);
    window.setTimeout(() => el.remove(), 3600);
  }

  function openModal(modalId) {
    const modal = $(modalId);
    if (!modal) {
      return;
    }
    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    const input = modal.querySelector("input:not([type='hidden'])");
    if (input) {
      window.setTimeout(() => input.focus(), 40);
    }
  }

  function closeModal(modal) {
    if (!modal) {
      return;
    }
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
  }

  function setMovementType(type) {
    if (!movementTypeInput || !movementModalTitle) {
      return;
    }
    movementTypeInput.value = type;
    movementModalTitle.textContent = type === "cash_out" ? "Salida de efectivo" : "Entrada de efectivo";
  }

  productSearch.addEventListener("input", filterProducts);
  productSearch.addEventListener("keydown", (event) => {
    if (event.key !== "Enter") {
      return;
    }
    event.preventDefault();
    const term = productSearch.value.trim().toLowerCase();
    const matches = filterProducts();
    const exact = products.find((product) => String(product.sku || "").toLowerCase() === term);
    const product = exact || matches[0];
    if (product) {
      addProduct(product);
      productSearch.select();
    }
  });

  clientSearch.addEventListener("input", filterClients);
  clientSearch.addEventListener("focus", filterClients);
  clientSearch.addEventListener("keydown", (event) => {
    if (event.key !== "Enter") {
      return;
    }
    event.preventDefault();
    const firstResult = clientResults.querySelector(".client-result");
    if (firstResult) {
      firstResult.click();
    }
  });

  clientResults.addEventListener("click", (event) => {
    const button = event.target.closest(".client-result");
    if (!button) {
      return;
    }
    const clientId = Number(button.dataset.clientId || 0);
    const customer = customers.find((entry) => Number(entry.id) === clientId);
    selectClient(customer || null);
  });

  $("clearClientBtn").addEventListener("click", () => selectClient(null));

  document.addEventListener("click", (event) => {
    if (!event.target.closest(".client-picker")) {
      clientResults.classList.remove("is-open");
    }
  });

  warehouseSelect.addEventListener("change", () => {
    warehouseInput.value = warehouseSelect.value;
    const url = new URL(window.location.href);
    url.searchParams.set("warehouse_id", warehouseSelect.value);
    url.searchParams.delete("receipt_id");
    window.location.href = url.toString();
  });

  amountReceived.addEventListener("input", () => {
    state.amountTouched = true;
    updatePaymentSummary();
    renderReceipt();
  });

  methodGrid.addEventListener("click", (event) => {
    const button = event.target.closest(".method-button");
    if (button) {
      setPaymentMethod(button.dataset.method);
      if (button.dataset.method !== "cash") {
        const totals = calcTotals();
        amountReceived.value = totals.total.toFixed(2);
        state.amountTouched = true;
        updatePaymentSummary();
      }
    }
  });

  $("clearCartBtn").addEventListener("click", clearCart);
  $("newSaleBtn").addEventListener("click", () => {
    window.location.href = config.newSaleUrl || window.location.pathname;
  });
  $("printReceiptBtn").addEventListener("click", () => printReceipt("sale"));
  $("drawerBtn").addEventListener("click", openDrawer);
  if ($("drawerPanelBtn")) {
    $("drawerPanelBtn").addEventListener("click", openDrawer);
  }
  checkoutForm.addEventListener("submit", prepareCheckout);

  document.querySelectorAll("[data-modal-open]").forEach((button) => {
    button.addEventListener("click", () => {
      if (button.dataset.movementType) {
        setMovementType(button.dataset.movementType);
      }
      openModal(button.dataset.modalOpen);
    });
  });

  document.querySelectorAll("[data-modal-close]").forEach((button) => {
    button.addEventListener("click", () => closeModal(button.closest(".modal-backdrop")));
  });

  document.querySelectorAll(".modal-backdrop").forEach((backdrop) => {
    backdrop.addEventListener("click", (event) => {
      if (event.target === backdrop) {
        closeModal(backdrop);
      }
    });
  });

  window.addEventListener("afterprint", () => {
    if (!pendingDrawerPrint) {
      return;
    }
    pendingDrawerPrint = false;
    showLocalFlash("Gaveta enviada a la impresora configurada.", "success");
  });

  window.setInterval(() => {
    $("cashierClock").textContent = new Date().toLocaleTimeString(locale, {
      hour: "2-digit",
      minute: "2-digit"
    });
  }, 1000);

  renderProducts(products);
  renderRegisterSummary();
  selectClient(null);
  if (checkoutBtn && !registerState.isOpen) {
    checkoutBtn.disabled = true;
  }
  renderCart();
  setPaymentMethod("cash");
  if (completedReceipt) {
    renderReceipt();
    window.setTimeout(() => printReceipt("sale"), 350);
  }
})();
