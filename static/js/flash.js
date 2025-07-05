document.addEventListener('DOMContentLoaded', function () {
    // Get all flash messages
    const flashMessages = document.querySelectorAll('.flash-message');

    // Add click event to close buttons
    document.querySelectorAll('.flash-close').forEach(button => {
        button.addEventListener('click', function () {
            const message = this.closest('.flash-message');
            message.classList.add('fade-out');
            setTimeout(() => {
                message.remove();
            }, 500);
        });
    });

    // Auto-dismiss messages after 5 seconds
    flashMessages.forEach(message => {
        setTimeout(() => {
            if (message) {
                message.classList.add('fade-out');
                setTimeout(() => {
                    message.remove();
                }, 500);
            }
        }, 5000);
    });
});