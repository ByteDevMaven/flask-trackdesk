const deleteModal = document.getElementById('delete-modal');
const deleteSupplierName = document.getElementById('delete-supplier-name');
const deleteForm = document.getElementById('delete-form');
const cancelDelete = document.getElementById('cancel-delete');

document.querySelectorAll('.delete-supplier').forEach(button => {
    button.addEventListener('click', function () {
        const id = this.getAttribute('data-id');
        const name = this.getAttribute('data-name');

        deleteSupplierName.textContent = name;
        deleteForm.action = "{{ url_for('suppliers.delete', supplier_id=0, company_id=selected_company_id) }}".replace('0', id);
        deleteModal.classList.remove('hidden');
    });
});

cancelDelete.addEventListener('click', function () {
    deleteModal.classList.add('hidden');
});

deleteModal.addEventListener('click', function (e) {
    if (e.target === deleteModal) {
        deleteModal.classList.add('hidden');
    }
});