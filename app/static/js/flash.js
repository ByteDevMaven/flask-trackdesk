document.addEventListener('DOMContentLoaded', function () {
    const flashMessages = document.querySelectorAll('.flash-message');

    document.querySelectorAll('.flash-close').forEach(button => {
        button.addEventListener('click', function () {
            const message = this.closest('.flash-message');
            message.classList.add('fade-out');
            setTimeout(() => {
                message.remove();
            }, 500);
        });
    });

    flashMessages.forEach(message => {
        setTimeout(() => {
            if (message) {
                message.classList.add('fade-out');
                setTimeout(() => {
                    message.remove();
                }, 500);
            }
        }, 8000);
    });
});