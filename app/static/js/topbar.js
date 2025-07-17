document.getElementById('company-menu-button').addEventListener('click', function () {
    var menu = document.getElementById('company-menu');
    menu.classList.toggle('hidden');
});

document.addEventListener('click', function (event) {
    var button = document.getElementById('company-menu-button');
    var menu = document.getElementById('company-menu');

    if (!button.contains(event.target) && !menu.contains(event.target)) {
        menu.classList.add('hidden');
    }
});

document.getElementById('user-menu-btn').addEventListener('click', function () {
    var menu = document.getElementById('user-dropdown');
    menu.classList.toggle('hidden');
});

document.addEventListener('click', function (event) {
    var button = document.getElementById('user-menu-btn');
    var menu = document.getElementById('user-dropdown');

    if (!button.contains(event.target) && !menu.contains(event.target)) {
        menu.classList.add('hidden');
    }
});