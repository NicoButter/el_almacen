(function () {
    function openTicketModal(id) {
        const scriptEl = document.getElementById('td-' + id);
        if (!scriptEl) return;
        const data = JSON.parse(scriptEl.textContent);

        document.getElementById('modal-ticket-id').textContent = '#' + data.id;
        document.getElementById('modal-cashier').textContent = data.cashier;
        document.getElementById('modal-cliente').textContent = data.cliente || '—';
        document.getElementById('modal-fecha').textContent = data.fecha;
        document.getElementById('modal-hora').textContent = data.hora;
        document.getElementById('modal-total').textContent = parseFloat(data.total).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

        // Tabla de ítems
        const tbody = document.getElementById('modal-items-body');
        tbody.innerHTML = '';
        if (data.items.length === 0) {
            const tr = document.createElement('tr');
            tr.innerHTML = '<td colspan="3" class="table-empty">Sin productos registrados.</td>';
            tbody.appendChild(tr);
        } else {
            data.items.forEach(function (item) {
                const unit = item.fraccionado ? 'grs.' : 'u.';
                const tr = document.createElement('tr');
                tr.innerHTML = '<td>' + item.name + '</td><td>' + item.qty + ' ' + unit + '</td><td class="col-amount">$' + parseFloat(item.subtotal).toLocaleString('es-AR', { minimumFractionDigits: 2 }) + '</td>';
                tbody.appendChild(tr);
            });
        }

        // Botón WhatsApp
        const waBtn = document.getElementById('modal-whatsapp-btn');
        if (data.hasPhone && data.phone) {
            const phone = data.phone.replace(/\D/g, '');
            let text = 'Hola ' + (data.cliente || 'cliente') + '! \uD83D\uDED2\n';
            text += 'Acá está el detalle de tu compra en *El Almacén*:\n\n';
            text += '*Ticket #' + data.id + '*\n';
            text += '\uD83D\uDCC5 ' + data.fecha + ' a las ' + data.hora + '\n';
            text += '\uD83D\uDC64 Cajero: ' + data.cashier + '\n\n';
            text += '*Productos:*\n';
            data.items.forEach(function (item) {
                const unit = item.fraccionado ? 'grs.' : 'u.';
                text += '\u2022 ' + item.name + ' \xD7' + item.qty + ' ' + unit + ': $' + item.subtotal + '\n';
            });
            text += '\n*Total: $' + data.total + '*\n\n\xA1Gracias por tu compra! \uD83D\uDE0A';
            waBtn.href = 'https://wa.me/' + phone + '?text=' + encodeURIComponent(text);
            waBtn.style.display = '';
        } else {
            waBtn.style.display = 'none';
        }

        // Botón Email
        const emailBtn = document.getElementById('modal-email-btn');
        if (data.hasEmail) {
            emailBtn.href = data.emailUrl;
            emailBtn.style.display = '';
        } else {
            emailBtn.style.display = 'none';
        }

        // Botón Reimprimir
        document.getElementById('modal-reprint-btn').href = data.reprintUrl;

        // Mostrar modal
        const overlay = document.getElementById('ticketModalOverlay');
        overlay.classList.add('is-open');
        overlay.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    }

    function closeTicketModal() {
        const overlay = document.getElementById('ticketModalOverlay');
        overlay.classList.remove('is-open');
        overlay.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }

    function handleOverlayClick(event) {
        if (event.target === document.getElementById('ticketModalOverlay')) {
            closeTicketModal();
        }
    }

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeTicketModal();
    });

    window.openTicketModal = openTicketModal;
    window.closeTicketModal = closeTicketModal;
    window.handleOverlayClick = handleOverlayClick;
})();
