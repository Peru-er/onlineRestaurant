
window.addEventListener('DOMContentLoaded', () => {
    const flashes = document.querySelectorAll('.flash');

    flashes.forEach(flash => {
        flash.style.opacity = '1';
        flash.classList.add('flash-visible');

        const timeoutId = setTimeout(() => {
            hideFlash(flash);
        }, 4000);

        flash.addEventListener('click', () => {
            clearTimeout(timeoutId);
            hideFlash(flash);
        });
    });

    function hideFlash(flash) {
        flash.classList.remove('flash-visible');
        flash.classList.add('flash-hide');

        setTimeout(() => {
            flash.remove();
        }, 500);
    }
});

