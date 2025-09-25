function showAddPaymentModal() {
    document.getElementById('addPaymentModal').classList.remove('hidden');
}

function hideAddPaymentModal() {
    document.getElementById('addPaymentModal').classList.add('hidden');
}

// Close modal when clicking outside
document.getElementById('addPaymentModal').addEventListener('click', function (e) {
    if (e.target === this) {
        hideAddPaymentModal();
    }
});