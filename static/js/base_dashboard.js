// Base Dashboard Scripts
function updateDateTime() {
    const now = new Date();
    const dateTimeString = now.toLocaleString('es-ES', { dateStyle: 'full', timeStyle: 'short' });
    const dateElement = document.getElementById('datetime');
    if (dateElement) {
        dateElement.textContent = dateTimeString;
    }
}

if (document.getElementById('datetime')) {
    updateDateTime();
    setInterval(updateDateTime, 1000);
}
