document.addEventListener('DOMContentLoaded', function () {
    var messages = document.querySelectorAll('.messages .alert');
    messages.forEach(function (message) {
        var duration = message.getAttribute('data-duration');
        if (duration) {
            setTimeout(function () {
                message.style.opacity = '0';
            }, parseInt(duration));
        }
    });
});