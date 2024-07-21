document.addEventListener("DOMContentLoaded", function() {
    const forms = document.querySelectorAll('.rate-review-form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            const authorId = form.getAttribute('data-author');
            const userId = form.getAttribute('data-user');
            if (authorId === userId) {
                event.preventDefault();
                 alert("You cannot like your own review.");
            }
        });
    });
});