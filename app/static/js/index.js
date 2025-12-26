document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const toggle = document.getElementById('sidebar-toggle');
    const labels = document.querySelectorAll('[data-sidebar-label]');

    if (!sidebar || !toggle) return;

    const apply = (collapsed) => {
        sidebar.dataset.collapsed = collapsed;
        labels.forEach(l => l.dataset.collapsed = collapsed);
        localStorage.setItem('sidebar-collapsed', collapsed);
    };

    apply(localStorage.getItem('sidebar-collapsed') === 'true');

    toggle.addEventListener('click', () => {
        apply(sidebar.dataset.collapsed !== 'true');
    });

    function bindDropdown(buttonId, menuId) {
        const btn = document.getElementById(buttonId);
        const menu = document.getElementById(menuId);

        if (!btn || !menu) return;

        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            menu.classList.remove('hidden');
        });

        document.addEventListener('click', (e) => {
            if (!btn.contains(e.target) && !menu.contains(e.target)) {
                menu.classList.add('hidden');
            }
        });
    }

    bindDropdown('language-menu-button', 'language-menu');
    bindDropdown('company-menu-button', 'company-menu');
    bindDropdown('user-menu-btn', 'user-dropdown');
});