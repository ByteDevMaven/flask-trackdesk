document.addEventListener('DOMContentLoaded', function () {
    const clientModal = document.getElementById('client-modal');
    const searchTrigger = document.getElementById('client-search-trigger');
    const closeBtn = document.getElementById('client-modal-close');
    const backdrop = document.getElementById('client-modal-backdrop');
    const searchInput = document.getElementById('client-search-input');
    const resultsContainer = document.getElementById('client-results-container');
    const resultsList = document.getElementById('client-results-list');
    const emptyState = document.getElementById('client-empty-state');
    const selectedNameSpan = document.getElementById('selected-client-name');
    const clientIdInput = document.getElementById('client_id');

    let searchTimeout;

    // Open modal
    searchTrigger.addEventListener('click', function () {
        clientModal.classList.remove('hidden');
        searchInput.focus();
    });

    // Close modal
    function closeModal() {
        clientModal.classList.add('hidden');
        searchInput.value = '';
        resultsList.innerHTML = '';
        resultsList.classList.add('hidden');
        emptyState.classList.remove('hidden');
        emptyState.textContent = "abc > 2";
    }

    closeBtn.addEventListener('click', closeModal);
    backdrop.addEventListener('click', closeModal);

    // Search functionality
    searchInput.addEventListener('input', function (e) {
        const query = e.target.value.trim();

        clearTimeout(searchTimeout);

        if (query.length < 2) {
            resultsList.classList.add('hidden');
            emptyState.classList.remove('hidden');
            emptyState.textContent = query.length === 0 ? "..." : "abc > 2";
            return;
        }

        searchTimeout = setTimeout(() => {
            const companyId = document.getElementById('company_id').value;
            fetch(`/${companyId}/clients/search?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    resultsList.innerHTML = '';

                    if (data.results && data.results.length > 0) {
                        emptyState.classList.add('hidden');
                        resultsList.classList.remove('hidden');

                        data.results.forEach(client => {
                            const li = document.createElement('li');
                            li.className = 'px-4 py-3 hover:bg-secondary-50 cursor-pointer transition flex justify-between items-center';
                            li.innerHTML = `
                                    <div>
                                        <div class="font-medium text-fg-base">${client.name}</div>
                                        <div class="text-xs text-fg-muted">${client.email || ''} ${client.identifier ? '• ' + client.identifier : ''}</div>
                                    </div>
                                    <i class="fas fa-check text-accent-500 opacity-0"></i>
                                `;

                            li.addEventListener('click', function () {
                                clientIdInput.value = client.id;
                                selectedNameSpan.textContent = client.name;
                                selectedNameSpan.classList.remove('text-fg-muted');
                                selectedNameSpan.classList.add('text-fg-base');
                                closeModal();
                            });

                            resultsList.appendChild(li);
                        });
                    } else {
                        resultsList.classList.add('hidden');
                        emptyState.classList.remove('hidden');
                        emptyState.textContent = "!!!";
                    }
                })
                .catch(error => {
                    console.error('Error searching clients:', error);
                    resultsList.classList.add('hidden');
                    emptyState.classList.remove('hidden');
                    emptyState.textContent = "ERROR!";
                });
        }, 300);
    });
});