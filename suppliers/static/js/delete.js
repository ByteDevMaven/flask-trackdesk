const deleteBtn = document.getElementById('delete-btn');
const deleteModal = document.getElementById('delete-modal');
const cancelDelete = document.getElementById('cancel-delete');

deleteBtn.addEventListener('click', function () {
    deleteModal.classList.remove('hidden');
});

cancelDelete.addEventListener('click', function () {
    deleteModal.classList.add('hidden');
});

deleteModal.addEventListener('click', function (e) {
    if (e.target === deleteModal) {
        deleteModal.classList.add('hidden');
    }
});