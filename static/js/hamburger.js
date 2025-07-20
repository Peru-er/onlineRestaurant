
document.addEventListener('DOMContentLoaded', function () {
    const hamburger = document.getElementById('hamburger');
    const navMenus = document.querySelectorAll('.nav-menu');

    hamburger.addEventListener('click', () => {
        navMenus.forEach(menu => {
            menu.classList.toggle('show');
        });
    });
});


