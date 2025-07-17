function confirmDelete(id, name) {
    document.getElementById('clientName').textContent = name;
    document.getElementById('deleteForm').action = "{{ url_for('customers.delete', company_id=company_id, id=0) }}".replace('0', id);
    document.getElementById('deleteModal').classList.remove('hidden');
}

function closeDeleteModal() {
    document.getElementById('deleteModal').classList.add('hidden');
}

// Close modal when clicking outside
document.getElementById('deleteModal').addEventListener('click', function (e) {
    if (e.target === this) {
        closeDeleteModal();
    }
});