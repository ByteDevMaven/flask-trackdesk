// ══════════════════════════════════════════════════════════════
//  STATE
// ══════════════════════════════════════════════════════════════
const state = {
    barcodeType: 'CODE128',  // 'CODE128' | 'QR'
    name: document.getElementById('f-name').value,
    sku: document.getElementById('f-sku').value,
    price: document.getElementById('f-price').value,
    showName: true,
    showPrice: true,
    showBcText: true,
    nameSize: 14,
    nameBold: true,
    nameAlign: 'center',
    priceSize: 13,
    priceBold: true,
    priceAlign: 'center',
    bcTextSize: 10,
    barWidth: 1.5,
    barHeight: 40,
    barMargin: 4,
    barColor: '#000000',
    bgColor: '#ffffff',
    lblW: 90,   // mm
    lblH: 40,   // mm
    padding: 6,
};

// ── Security: allowlist of valid state keys to prevent prototype pollution ──
// Only keys present in this set may be written to `state` via bracket notation.
const STATE_KEYS = Object.freeze(new Set(Object.keys(state)));

/**
 * Safely assign a value to state, rejecting any key that is not in STATE_KEYS.
 * This prevents prototype-pollution attacks via bracket-object notation.
 * @param {string} key  - Must be a known state property name.
 * @param {*}      value - The validated value to assign.
 */
function safeSetState(key, value) {
    if (!STATE_KEYS.has(key)) {
        // Key is not a recognised state property — drop silently.
        return;
    }
    state[key] = value;
}

// Undo/Redo stacks
const history = { stack: [structuredClone(state)], idx: 0 };

function pushHistory() {
    history.stack = history.stack.slice(0, history.idx + 1);
    history.stack.push(structuredClone(state));
    history.idx = history.stack.length - 1;
    syncUndoRedo();
}
function undo() {
    if (history.idx > 0) {
        history.idx--;
        const restored = structuredClone(history.stack[history.idx]);
        for (const [k, v] of Object.entries(restored)) { safeSetState(k, v); }
        syncAllControls(); render(); syncUndoRedo();
    }
}
function redo() {
    if (history.idx < history.stack.length - 1) {
        history.idx++;
        const restored = structuredClone(history.stack[history.idx]);
        for (const [k, v] of Object.entries(restored)) { safeSetState(k, v); }
        syncAllControls(); render(); syncUndoRedo();
    }
}
function syncUndoRedo() {
    document.getElementById('btn-undo').disabled = history.idx <= 0;
    document.getElementById('btn-redo').disabled = history.idx >= history.stack.length - 1;
}

// ══════════════════════════════════════════════════════════════
//  RENDER LABEL
// ══════════════════════════════════════════════════════════════
const MM_TO_PX = 3.7795; // 96dpi

function buildLabelDOM(s, forPrint = false) {
    const w = Math.round(s.lblW * MM_TO_PX);
    const h = Math.round(s.lblH * MM_TO_PX);

    const card = document.createElement('div');
    card.className = 'label-card';
    card.style.cssText = `
        width:${w}px; height:${h}px;
        background:${s.bgColor};
        padding:${s.padding}px;
        gap:2px;
        justify-content:center;
    `;

    // Name
    if (s.showName) {
        const el = document.createElement('div');
        el.className = 'label-name';
        el.textContent = s.name;
        el.style.cssText = `
            font-size:${s.nameSize}px;
            line-height:${s.nameSize * 1.35}px;
            font-weight:${s.nameBold ? '700' : '400'};
            text-align:${s.nameAlign};
            color:${s.barColor};
            padding-top:2px;
            padding-bottom:2px;
            display:-webkit-box;
            -webkit-line-clamp:2;
            -webkit-box-orient:vertical;
        `;
        card.appendChild(el);
    }

    // Barcode / QR
    const bcWrap = document.createElement('div');
    bcWrap.className = 'label-barcode-wrap';
    bcWrap.style.cssText = 'flex:1; display:flex; align-items:center; justify-content:center; min-height:0; overflow:hidden;';

    if (s.barcodeType === 'QR') {
        const qrCanvas = document.createElement('canvas');
        const qrSide = Math.min(w - s.padding * 2, h - s.padding * 2 - 40) || 60;
        qrCanvas.width = qrSide;
        qrCanvas.height = qrSide;
        bcWrap.appendChild(qrCanvas);
        card.appendChild(bcWrap);
        // Render QR async after element is in DOM
        card._qrCanvas = qrCanvas;
        card._qrValue = s.sku;
        card._qrSize = qrSide;
    } else {
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.style.cssText = 'max-width:100%; height:auto;';
        bcWrap.appendChild(svg);
        card.appendChild(bcWrap);
        card._barcodeSVG = svg;
        card._barcodeValue = s.sku;
        card._barcodeOpts = {
            format: 'CODE128',
            width: s.barWidth,
            height: s.barHeight,
            margin: s.barMargin,
            fontSize: s.bcTextSize,
            displayValue: s.showBcText,
            lineColor: s.barColor,
            background: s.bgColor,
        };
    }

    // Price
    if (s.showPrice) {
        const el = document.createElement('div');
        el.className = 'label-price';
        el.textContent = s.price;
        el.style.cssText = `
            font-size:${s.priceSize}px;
            line-height: ${s.priceSize * 1.15}px;
            font-weight:${s.priceBold ? '700' : '400'};
            text-align:${s.priceAlign};
            color:${s.barColor};
        `;
        card.appendChild(el);
    }

    return card;
}

function applyBarcodes(container) {
    // Apply JsBarcode
    container.querySelectorAll('[data-bc-pending]').forEach(svg => {
        // Already handled via _barcodeSVG
    });

    // Walk all label-cards
    container.querySelectorAll('.label-card').forEach(card => {
        if (card._barcodeSVG && card._barcodeValue) {
            try {
                JsBarcode(card._barcodeSVG, card._barcodeValue, card._barcodeOpts);
            } catch (e) {
                card._barcodeSVG.setAttribute('width', '10');
            }
        }
        if (card._qrCanvas) {
            QRCode.toCanvas(card._qrCanvas, card._qrValue || '0', { width: card._qrSize, margin: 1 }, () => { });
        }
    });
}

let renderTimer = null;
function render() {
    clearTimeout(renderTimer);
    renderTimer = setTimeout(_doRender, 30);
}

function _doRender() {
    const zoom = document.getElementById('zoom-slider').value / 100;
    const wrap = document.getElementById('preview-wrap');
    const preview = document.getElementById('label-preview');

    // Build fresh label
    const label = buildLabelDOM(state);
    label.id = 'label-preview';
    label.style.transform = `scale(${zoom})`;
    label.style.transformOrigin = 'top center';

    wrap.replaceChild(label, preview);
    applyBarcodes(wrap);
}

// ══════════════════════════════════════════════════════════════
//  WIRE CONTROLS
// ══════════════════════════════════════════════════════════════
function bindInput(id, key, transform) {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener('input', () => {
        safeSetState(key, transform ? transform(el.value) : el.value);
        render();
    });
    el.addEventListener('change', () => { pushHistory(); });
}
function bindRange(id, key, displayId, suffix = '') {
    const el = document.getElementById(id);
    const disp = document.getElementById(displayId);
    if (!el) return;
    el.addEventListener('input', () => {
        const v = parseFloat(el.value);
        safeSetState(key, v);
        if (disp) disp.textContent = v + suffix;
        render();
    });
    el.addEventListener('change', pushHistory);
}
function bindCheck(id, key) {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener('change', () => { safeSetState(key, el.checked); render(); pushHistory(); });
}
function bindSelect(id, key) {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener('change', () => { safeSetState(key, el.value); render(); pushHistory(); });
}

// Inputs
bindInput('f-name', 'name');
bindInput('f-sku', 'sku');
bindInput('f-price', 'price');
bindInput('lbl-w', 'lblW', Number);
bindInput('lbl-h', 'lblH', Number);

// Ranges
bindRange('name-size', 'nameSize', 'val-name-size', 'px');
bindRange('price-size', 'priceSize', 'val-price-size', 'px');
bindRange('bc-text-size', 'bcTextSize', 'val-bc-size', 'px');
bindRange('bar-width', 'barWidth', 'val-bw');
bindRange('bar-height', 'barHeight', 'val-bh', 'px');
bindRange('bar-margin', 'barMargin', 'val-margin', 'px');
bindRange('lbl-pad', 'padding', 'val-pad', 'px');

// Checkboxes
bindCheck('show-name', 'showName');
bindCheck('show-price', 'showPrice');
bindCheck('show-bcode-text', 'showBcText');
bindCheck('name-bold', 'nameBold');
bindCheck('price-bold', 'priceBold');

// Selects
bindSelect('name-align', 'nameAlign');
bindSelect('price-align', 'priceAlign');

// Color inputs
['bar-color', 'bg-color'].forEach(id => {
    const el = document.getElementById(id);
    const key = id === 'bar-color' ? 'barColor' : 'bgColor';
    el.addEventListener('input', () => { state[key] = el.value; render(); });
    el.addEventListener('change', pushHistory);
});

// Zoom
const zoomEl = document.getElementById('zoom-slider');
zoomEl.addEventListener('input', () => {
    document.getElementById('zoom-val').textContent = zoomEl.value + '%';
    render();
});

// Label size presets
document.querySelectorAll('.size-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        state.lblW = +btn.dataset.w;
        state.lblH = +btn.dataset.h;
        document.getElementById('lbl-w').value = state.lblW;
        document.getElementById('lbl-h').value = state.lblH;
        render(); pushHistory();
    });
});

// Barcode type toggle
document.querySelectorAll('.type-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        state.barcodeType = btn.dataset.type;
        document.querySelectorAll('.type-btn').forEach(b => {
            b.classList.toggle('active', b === btn);
        });
        render(); pushHistory();
    });
});

// Tabs
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tab = btn.dataset.tab;
        document.querySelectorAll('.tab-btn').forEach(b => {
            b.classList.toggle('active', b === btn);
        });
        document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));
        document.getElementById('tab-' + tab).classList.remove('hidden');
    });
});

// Undo/Redo buttons
document.getElementById('btn-undo').addEventListener('click', undo);
document.getElementById('btn-redo').addEventListener('click', redo);
document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'z') { e.preventDefault(); undo(); }
    if ((e.ctrlKey || e.metaKey) && e.key === 'y') { e.preventDefault(); redo(); }
});

// ══════════════════════════════════════════════════════════════
//  EXPORT: PNG
// ══════════════════════════════════════════════════════════════
document.getElementById('btn-png').addEventListener('click', async () => {
    const label = buildLabelDOM(state);
    label.style.position = 'fixed';
    label.style.top = '-9999px';
    document.body.appendChild(label);
    applyBarcodes(document.body);
    await new Promise(r => setTimeout(r, 250));
    const canvas = await html2canvas(label, {
        scale: 3,
        backgroundColor: state.bgColor,
        onclone: (doc) => {
            const svgs = doc.querySelectorAll('svg');
            svgs.forEach(svg => {
                svg.style.maxWidth = 'none';
            });
        }
    });
    document.body.removeChild(label);
    const a = document.createElement('a');
    a.href = canvas.toDataURL('image/png');
    a.download = `label_${state.sku}.png`;
    a.click();
});

// ══════════════════════════════════════════════════════════════
//  EXPORT: Single PDF
// ══════════════════════════════════════════════════════════════
document.getElementById('btn-pdf').addEventListener('click', async () => {
    const label = buildLabelDOM(state);
    label.style.position = 'fixed';
    label.style.top = '-9999px';
    document.body.appendChild(label);
    applyBarcodes(document.body);
    await document.fonts.ready;
    const canvas = await html2canvas(label, {
        scale: 3,
        backgroundColor: state.bgColor,
        onclone: (doc) => {
            const svgs = doc.querySelectorAll('svg');
            svgs.forEach(svg => {
                svg.style.maxWidth = 'none';
                svg.style.height = '100%';
            });
        }
    });
    document.body.removeChild(label);
    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF({ orientation: state.lblW > state.lblH ? 'l' : 'p', unit: 'mm', format: [state.lblW, state.lblH] });
    pdf.addImage(canvas.toDataURL('image/png'), 'PNG', 0, 0, state.lblW, state.lblH);
    pdf.save(`label_${state.sku}.pdf`);
});

// ══════════════════════════════════════════════════════════════
//  PRINT: browser print
// ══════════════════════════════════════════════════════════════
document.getElementById('btn-print').addEventListener('click', () => {
    buildPrintArea(1, +document.getElementById('bulk-cols').value || 1);
    window.print();
});

// ══════════════════════════════════════════════════════════════
//  BULK
// ══════════════════════════════════════════════════════════════
function buildBulkGrid(copies, cols, gap, container) {
    container.innerHTML = '';
    container.style.cssText = `
        display:grid;
        grid-template-columns:repeat(${cols}, max-content);
        gap:${gap}px;
        justify-content:center;
    `;
    for (let i = 0; i < copies; i++) {
        const lbl = buildLabelDOM(state);
        container.appendChild(lbl);
    }
    applyBarcodes(container);
}

function buildPrintArea(copies, cols) {
    const pa = document.getElementById('print-area');
    pa.style.cssText = `display:grid; grid-template-columns:repeat(${cols},1fr); gap:4mm; padding:6mm; box-sizing:border-box;`;
    pa.innerHTML = '';
    for (let i = 0; i < copies; i++) {
        pa.appendChild(buildLabelDOM(state, true));
    }
    applyBarcodes(pa);
}

document.getElementById('btn-bulk-preview').addEventListener('click', () => {
    const copies = +document.getElementById('bulk-copies').value || 12;
    const cols = +document.getElementById('bulk-cols').value || 3;
    const gap = +document.getElementById('bulk-gap').value || 8;
    buildBulkGrid(copies, cols, gap, document.getElementById('bulk-grid'));
    document.getElementById('single-preview-area').style.display = 'none';
    document.getElementById('bulk-preview-area').style.display = 'flex';
});

document.getElementById('btn-close-bulk').addEventListener('click', () => {
    document.getElementById('bulk-preview-area').style.display = 'none';
    document.getElementById('single-preview-area').style.display = 'flex';
});

document.getElementById('btn-bulk-print').addEventListener('click', () => {
    const copies = +document.getElementById('bulk-copies').value || 12;
    const cols = +document.getElementById('bulk-cols').value || 3;
    buildPrintArea(copies, cols);
    window.print();
});

document.getElementById('btn-bulk-pdf').addEventListener('click', async () => {
    const copies = +document.getElementById('bulk-copies').value || 12;
    const cols = +document.getElementById('bulk-cols').value || 3;
    const gap = +document.getElementById('bulk-gap').value || 8;
    const container = document.createElement('div');
    container.style.position = 'fixed';
    container.style.top = '-9999px';
    document.body.appendChild(container);
    buildBulkGrid(copies, cols, gap, container);
    await new Promise(r => setTimeout(r, 300));
    const canvas = await html2canvas(container, {
        scale: 2,
        backgroundColor: '#ffffff',
        onclone: (doc) => {
            const svgs = doc.querySelectorAll('svg');
            svgs.forEach(svg => {
                svg.style.maxWidth = 'none';
                svg.style.height = '100%';
            });
        }
    });
    document.body.removeChild(container);
    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF({ orientation: 'p', unit: 'mm', format: 'letter' });
    const pageW = pdf.internal.pageSize.getWidth();
    const pageH = pdf.internal.pageSize.getHeight();
    const ratio = canvas.width / canvas.height;
    const imgW = pageW - 20;
    const imgH = imgW / ratio;
    pdf.addImage(canvas.toDataURL('image/png'), 'PNG', 10, 10, imgW, Math.min(imgH, pageH - 20));
    pdf.save(`bulk_labels_${state.sku}.pdf`);
});

// ══════════════════════════════════════════════════════════════
//  TEMPLATES (localStorage)
// ══════════════════════════════════════════════════════════════
const TPL_KEY = 'bc_templates';

function loadTemplates() {
    return JSON.parse(localStorage.getItem(TPL_KEY) || '[]');
}
function saveTemplates(tpls) {
    localStorage.setItem(TPL_KEY, JSON.stringify(tpls));
}
function renderTemplateList() {
    const list = document.getElementById('tpl-list');
    const tpls = loadTemplates();
    if (!tpls.length) {
        list.innerHTML = '<p class="bc-empty">No hay plantillas guardadas.</p>';
        return;
    }
    list.innerHTML = '';
    tpls.forEach((tpl, i) => {
        const card = document.createElement('div');
        card.className = 'tpl-card';
        
        // Use textContent to avoid XSS in template names
        const nameText = tpl.name || 'Plantilla ' + (i + 1);
        const sizeText = `${tpl.lblW}×${tpl.lblH}mm`;

        const flexDiv = document.createElement('div');
        flexDiv.style.cssText = 'flex:1;min-width:0';
        
        const nameDiv = document.createElement('div');
        nameDiv.className = 'tpl-name';
        nameDiv.textContent = nameText;
        
        const sizeDiv = document.createElement('div');
        sizeDiv.className = 'tpl-size';
        sizeDiv.textContent = sizeText;
        
        flexDiv.appendChild(nameDiv);
        flexDiv.appendChild(sizeDiv);
        
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'tpl-actions';
        
        const loadBtn = document.createElement('button');
        loadBtn.className = 'tpl-load';
        loadBtn.dataset.idx = i;
        loadBtn.textContent = 'Cargar';
        
        const copyBtn = document.createElement('button');
        copyBtn.className = 'tpl-copy';
        copyBtn.dataset.idx = i;
        copyBtn.textContent = 'Dupl.';
        
        const delBtn = document.createElement('button');
        delBtn.className = 'tpl-del';
        delBtn.dataset.idx = i;
        delBtn.textContent = '✕';
        
        actionsDiv.appendChild(loadBtn);
        actionsDiv.appendChild(copyBtn);
        actionsDiv.appendChild(delBtn);
        
        card.appendChild(flexDiv);
        card.appendChild(actionsDiv);
        
        list.appendChild(card);
    });
    list.querySelectorAll('.tpl-load').forEach(btn => {
        btn.addEventListener('click', () => {
            const tpl = loadTemplates()[+btn.dataset.idx];
            for (const [k, v] of Object.entries(tpl)) { safeSetState(k, v); }
            syncAllControls();
            render();
            pushHistory();
        });
    });
    list.querySelectorAll('.tpl-copy').forEach(btn => {
        btn.addEventListener('click', () => {
            const tpls = loadTemplates();
            const clone = { ...tpls[+btn.dataset.idx], name: tpls[+btn.dataset.idx].name + ' (copy)' };
            tpls.push(clone);
            saveTemplates(tpls);
            renderTemplateList();
        });
    });
    list.querySelectorAll('.tpl-del').forEach(btn => {
        btn.addEventListener('click', () => {
            const tpls = loadTemplates();
            tpls.splice(+btn.dataset.idx, 1);
            saveTemplates(tpls);
            renderTemplateList();
        });
    });
}

document.getElementById('btn-save-tpl').addEventListener('click', () => {
    const tplName = prompt('Nombre de plantilla:', state.name || 'Mi Plantilla');
    if (tplName === null) return;
    const tpls = loadTemplates();
    tpls.push({ ...structuredClone(state), name: tplName });
    saveTemplates(tpls);
    renderTemplateList();
});

// ══════════════════════════════════════════════════════════════
//  SYNC CONTROLS → STATE (for undo/redo restore)
// ══════════════════════════════════════════════════════════════
function syncAllControls() {
    const s = state;
    const set = (id, v) => { const el = document.getElementById(id); if (el) el.value = v; };
    const setChk = (id, v) => { const el = document.getElementById(id); if (el) el.checked = v; };

    set('f-name', s.name); set('f-sku', s.sku); set('f-price', s.price);
    set('lbl-w', s.lblW); set('lbl-h', s.lblH);
    set('name-size', s.nameSize); document.getElementById('val-name-size').textContent = s.nameSize + 'px';
    set('price-size', s.priceSize); document.getElementById('val-price-size').textContent = s.priceSize + 'px';
    set('bc-text-size', s.bcTextSize); document.getElementById('val-bc-size').textContent = s.bcTextSize + 'px';
    set('bar-width', s.barWidth); document.getElementById('val-bw').textContent = s.barWidth;
    set('bar-height', s.barHeight); document.getElementById('val-bh').textContent = s.barHeight + 'px';
    set('bar-margin', s.barMargin); document.getElementById('val-margin').textContent = s.barMargin + 'px';
    set('lbl-pad', s.padding); document.getElementById('val-pad').textContent = s.padding + 'px';
    set('bar-color', s.barColor); set('bg-color', s.bgColor);
    set('name-align', s.nameAlign); set('price-align', s.priceAlign);
    setChk('show-name', s.showName); setChk('show-price', s.showPrice); setChk('show-bcode-text', s.showBcText);
    setChk('name-bold', s.nameBold); setChk('price-bold', s.priceBold);
}

// ══════════════════════════════════════════════════════════════
//  INIT
// ══════════════════════════════════════════════════════════════
renderTemplateList();
render();