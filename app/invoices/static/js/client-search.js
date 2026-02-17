document.addEventListener('DOMContentLoaded', function () {
    const clientModal = document.getElementById('client-modal');
    const searchTrigger = document.getElementById('client-search-trigger');
    const closeBtn = document.getElementById('client-modal-close');
    const closeIcon = document.getElementById('client-modal-close-icon');
    const backdrop = document.getElementById('client-modal-backdrop');
    const searchInput = document.getElementById('client-search-input');
    const resultsContainer = document.getElementById('client-results-container');
    const resultsList = document.getElementById('client-results-list');
    const emptyState = document.getElementById('client-empty-state');
    const selectedNameSpan = document.getElementById('selected-client-name');
    const clientIdInput = document.getElementById('client_id');
    const companyIdInput = document.getElementById('company_id');

    let searchTimeout;

    // Open modal
    if (searchTrigger) {
        searchTrigger.addEventListener('click', function () {
            clientModal.classList.remove('hidden');
            // Small delay to ensure modal is visible before focusing
            setTimeout(() => {
                searchInput.focus();
            }, 50);
        });
    }

    // Close modal function
    function closeModal() {
        clientModal.classList.add('hidden');
        searchInput.value = '';
        resultsList.innerHTML = '';
        resultsList.classList.add('hidden');
        emptyState.classList.remove('hidden');
        // Reset empty state text
        emptyState.innerHTML = `
            <div class="mb-3 p-3 bg-slate-800 rounded-full shadow-sm inline-block">
                <i class="fas fa-users text-2xl text-slate-600"></i>
            </div>
            <span class="font-medium text-slate-400 block mb-1">Start searching</span>
            <span class="text-xs text-slate-500">Type name, email or phone number</span>
        `;
    }

    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (closeIcon) closeIcon.addEventListener('click', closeModal);
    if (backdrop) backdrop.addEventListener('click', closeModal);

    // Close on Escape key
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && !clientModal.classList.contains('hidden')) {
            closeModal();
        }
    });

    // Search functionality
    if (searchInput) {
        searchInput.addEventListener('input', function (e) {
            const query = e.target.value.trim();

            clearTimeout(searchTimeout);

            if (query.length < 2) {
                resultsList.classList.add('hidden');
                emptyState.classList.remove('hidden');
                return;
            }

            // Show loading state
            // ... (could add a spinner here if desired)

            searchTimeout = setTimeout(() => {
                const companyId = companyIdInput ? companyIdInput.value : '';
                if (!companyId) return;

                fetch(`/${companyId}/clients/search?q=${encodeURIComponent(query)}`)
                    .then(response => {
                        if (!response.ok) throw new Error('Network response was not ok');
                        return response.json();
                    })
                    .then(data => {
                        resultsList.innerHTML = '';

                        if (data.results && data.results.length > 0) {
                            emptyState.classList.add('hidden');
                            resultsList.classList.remove('hidden');

                            data.results.forEach(client => {
                                const li = document.createElement('li');
                                li.className = 'px-4 py-3 hover:bg-slate-700/50 cursor-pointer transition flex justify-between items-center group border-b border-slate-700/50 last:border-0';

                                // Highlight matching text could be added here

                                li.innerHTML = `
                                        <div class="flex items-center">
                                            <div class="h-8 w-8 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-400 mr-3">
                                                <span class="text-xs font-bold">${client.name.substring(0, 2).toUpperCase()}</span>
                                            </div>
                                            <div>
                                                <div class="font-medium text-slate-200 group-hover:text-indigo-400 transition-colors">${client.name}</div>
                                                <div class="text-xs text-slate-400">
                                                    ${client.email ? `<span class="mr-2"><i class="fas fa-envelope mr-1 text-slate-500"></i>${client.email}</span>` : ''}
                                                    ${client.identifier ? `<span><i class="fas fa-id-card mr-1 text-slate-500"></i>${client.identifier}</span>` : ''}
                                                </div>
                                            </div>
                                        </div>
                                        <i class="fas fa-chevron-right text-slate-500 group-hover:text-indigo-400 transition-colors text-xs"></i>
                                    `;

                                li.addEventListener('click', function () {
                                    if (clientIdInput) clientIdInput.value = client.id;
                                    if (selectedNameSpan) {
                                        selectedNameSpan.textContent = client.name;
                                        selectedNameSpan.classList.remove('text-slate-400'); // Remove placeholder style
                                        selectedNameSpan.classList.add('text-slate-200', 'font-medium'); // Add selected style
                                    }
                                    closeModal();

                                    // Trigger a custom event if needed for other parts of the form
                                    const event = new CustomEvent('client-selected', { detail: client });
                                    document.dispatchEvent(event);
                                });

                                resultsList.appendChild(li);
                            });
                        } else {
                            resultsList.classList.add('hidden');
                            emptyState.classList.remove('hidden');
                            emptyState.innerHTML = `
                                <div class="mb-2"><i class="far fa-sad-tear text-2xl text-slate-600"></i></div>
                                <span class="text-slate-400">No clients found</span>
                            `;
                        }
                    })
                    .catch(error => {
                        console.error('Error searching clients:', error);
                        resultsList.classList.add('hidden');
                        emptyState.classList.remove('hidden');
                        emptyState.innerHTML = `<span class="text-rose-400">Error searching clients. Please try again.</span>`;
                    });
            }, 300);
        });
    }
});