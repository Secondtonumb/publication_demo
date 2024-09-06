// script.js
document.querySelectorAll('.accordion-button').forEach(button => {
    button.addEventListener('click', () => {
        // Toggle the active class on the button
        button.classList.toggle('active');

        // Get the associated content
        const content = button.nextElementSibling;

        // Toggle the display of the content
        if (content.style.display === 'block') {
            content.style.display = 'none';
        } else {
            // Hide all other contents
            document.querySelectorAll('.accordion-content').forEach(item => {
                item.style.display = 'none';
                item.previousElementSibling.classList.remove('active');
            });
            // Show the clicked content
            content.style.display = 'block';
        }
    });
});