// tab switching - ticket_list
document.addEventListener('DOMContentLoaded', function () {
    const tabs = document.querySelectorAll('.summary-tab');
    const totalDisplay = document.getElementById('summary-total');
    const countDisplay = document.getElementById('summary-count');

    tabs.forEach(tab => {
        tab.addEventListener('click', function () {
            tabs.forEach(t => t.classList.remove('is-active'));
            this.classList.add('is-active');

            const total = this.getAttribute('data-total');
            const count = this.getAttribute('data-count');

            totalDisplay.parentElement.classList.add('updating');
            countDisplay.classList.add('updating');

            setTimeout(() => {
                totalDisplay.textContent = total;
                countDisplay.textContent = count;
                totalDisplay.parentElement.classList.remove('updating');
                countDisplay.classList.remove('updating');
            }, 200);
        });
    });
});
