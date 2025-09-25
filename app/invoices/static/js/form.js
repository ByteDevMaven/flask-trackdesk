document.addEventListener('DOMContentLoaded', () => {
    const itemsContainer = document.getElementById('items-container');
    const addItemBtn = document.getElementById('add-item');
    let itemIndex = itemsContainer.children.length;
    const currency = document.getElementById('currencySymbol').value;
    csrftoken = document.querySelector('input[name="csrf_token"]').value;

    addItemBtn.addEventListener('click', async () => {
        const formData = new FormData();
        formData.append('index', itemIndex);
        formData.append('csrf_token', csrftoken);

        const res = await fetch('/invoices/item-row', {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });

        const html = await res.text();
        const temp = document.createElement('tbody');
        temp.innerHTML = html;
        const row = temp.querySelector('tr');

        if (row) {
            itemsContainer.appendChild(row);
            itemIndex++;
            row.querySelector('.item-select')?.focus();
            updateRowTotal(row);
            updateTotals();
        }
    });

    itemsContainer.addEventListener('click', (e) => {
        if (e.target.closest('.remove-item')) {
            const row = e.target.closest('.item-row');
            if (itemsContainer.children.length > 1) {
                row.remove();
                updateTotals();
            } else {
                alert("At least one item is required");
            }
        }
    });

    itemsContainer.addEventListener('input', (e) => {
        if (e.target.matches('.item-quantity, .item-price')) {
            updateRowTotal(e.target.closest('.item-row'));
            updateTotals();
        }
    });

    itemsContainer.addEventListener('change', (e) => {
        if (e.target.classList.contains('item-select')) {
            const selected = e.target.selectedOptions[0];
            const row = e.target.closest('.item-row');

            // Auto-fill price
            const price = selected?.dataset?.price || '0.00';
            row.querySelector('.item-price').value = parseFloat(price).toFixed(2);

            // Auto-fill description
            const desc = selected?.dataset?.description || '';
            row.querySelector('.item-description').value = desc;

            const stock = selected?.dataset?.stock || '0';
            row.querySelector('.item-quantity').setAttribute('max', stock);

            updateRowTotal(row);
            updateTotals();
        }
    });

    function updateRowTotal(row) {
        const q = parseFloat(row.querySelector('.item-quantity')?.value || 0);
        const p = parseFloat(row.querySelector('.item-price')?.value || 0);
        row.querySelector('.item-total').textContent = currency + (q * p).toFixed(2);
    }

    function updateTotals() {
        let subtotal = 0;
        document.querySelectorAll('.item-row').forEach(row => {
            const q = parseFloat(row.querySelector('.item-quantity')?.value || 0);
            const p = parseFloat(row.querySelector('.item-price')?.value || 0);
            subtotal += q * p;
        });

        const tax15 = subtotal * 0.15;
        const tax18 = subtotal * 0;
        const total = subtotal + tax15 + tax18;

        document.getElementById('subtotal').textContent = currency + subtotal.toFixed(2);
        document.getElementById('tax-15').textContent = currency + tax15.toFixed(2);
        document.getElementById('tax-18').textContent = currency + tax18.toFixed(2);
        document.getElementById('total').textContent = currency + total.toFixed(2);
    }

    document.querySelectorAll('.item-row').forEach(updateRowTotal);
    updateTotals();
});