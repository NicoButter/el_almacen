// Reloj en tiempo real
function updateClock() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('es-AR', { hour12: false });
    document.getElementById('live-clock').textContent = timeStr;
}
setInterval(updateClock, 1000);
updateClock();

// Voice & Scanner Logic
document.addEventListener('DOMContentLoaded', function () {
    const modoVozBtn = document.getElementById('botonVoz');
    const indicador = document.getElementById('indicador');
    const vozText = document.getElementById('voz-text');

    let modoVozActivo = false;

    modoVozBtn.addEventListener('click', function () {
        modoVozActivo = !modoVozActivo;

        if (modoVozActivo) {
            vozText.textContent = 'Apagar Voz';
            indicador.style.display = 'block';
            modoVozBtn.style.color = '#ff3b3b';
            modoVozBtn.style.borderColor = '#ff3b3b';
        } else {
            vozText.textContent = 'Voz';
            indicador.style.display = 'none';
            modoVozBtn.style.color = 'inherit';
            modoVozBtn.style.borderColor = 'transparent';
        }
    });

    // Background video fallback
    const videoBg = document.getElementById('video-bg');
    if (videoBg) {
        const playVideo = () => {
            videoBg.play().catch(e => console.log('Video intro err:', e));
        };
        playVideo();
        setTimeout(playVideo, 1000);
    }
});

// Scanner initialization
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const context = canvas ? canvas.getContext('2d') : null;
const scanStatus = document.getElementById('scan-status');
let scanningEnabled = true;
let isProcessingCode = false;

if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
        .then((stream) => {
            if (video) {
                video.srcObject = stream;
                video.setAttribute('playsinline', true);
                if (typeof jsQR !== 'undefined') {
                    requestAnimationFrame(scanQRCode);
                } else {
                    scanStatus.textContent = 'Librería jsQR no cargada';
                }
            }
        })
        .catch((err) => {
            console.error('Error cámara:', err);
            if (scanStatus) scanStatus.textContent = 'No se detectó cámara';
        });
}

function scanQRCode() {
    if (!scanningEnabled || !video || !canvas || video.readyState !== video.HAVE_ENOUGH_DATA) {
        if (!isProcessingCode) requestAnimationFrame(scanQRCode);
        return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
    const code = jsQR(imageData.data, imageData.width, imageData.height, {
        inversionAttempts: 'dontInvert',
    });

    if (code && !isProcessingCode) {
        isProcessingCode = true;

        scanStatus.textContent = 'Procesando...';
        scanStatus.style.color = 'var(--base-foreground)';

        const feedbackOverlay = document.getElementById('product-feedback');
        const feedbackText = document.getElementById('feedback-text');
        const feedbackImg = document.getElementById('feedback-img');

        feedbackOverlay.style.display = 'flex';
        feedbackText.textContent = 'Buscando... (' + code.data + ')';
        feedbackText.style.color = 'var(--base-foreground)';
        feedbackImg.style.display = 'none';

        fetch('/sales/api/productos/' + code.data + '/')
            .then(response => {
                if (!response.ok) throw new Error('Producto No Encontrado');
                return response.json();
            })
            .then(producto => {
                if (producto.imagen) {
                    feedbackImg.src = producto.imagen;
                    feedbackImg.style.display = 'block';
                }
                feedbackText.textContent = producto.nombre;
                feedbackText.style.color = '#10b981';

                const detailsCard = document.getElementById('scanned-product-details');
                const detailsContent = document.getElementById('details-content-body');
                if (detailsCard && detailsContent) {
                    detailsCard.style.display = 'block';

                    const marca = producto.marca || 'S/M';
                    const categoria = producto.categoria__nombre || producto.categoria || '-';
                    const descripcion = producto.descripcion || 'Sin descripción adicional cargada.';

                    detailsContent.innerHTML = `
                        <h4 style="color: var(--base-primary); margin: 0 0 5px 0; font-size: 1.1rem;">${producto.nombre}</h4>
                        <div style="font-size: 0.85rem; color: var(--base-muted-foreground); margin-bottom: 12px; display:flex; gap: 10px;">
                            <span style="background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px;">${marca}</span>
                            <span style="background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px;">${categoria}</span>
                        </div>
                        <p style="font-size: 0.8rem; color: var(--base-foreground-muted); line-height: 1.3; margin-bottom: 10px; opacity: 0.8;">
                            ${descripcion}
                        </p>
                        <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px dashed rgba(255,255,255,0.1); padding-top: 10px;">
                            <div style="display: flex; flex-direction: column;">
                                <span style="font-size: 0.75rem; color: var(--base-muted-foreground); text-transform: uppercase;">Stock Actual</span>
                                <span style="font-weight: bold; color: ${producto.cantidad_stock > 5 ? '#10b981' : '#f59e0b'};">
                                    ${producto.cantidad_stock !== undefined ? producto.cantidad_stock : '?'}
                                    <span style="font-size: 0.75rem;">${producto.unidad_medida || 'UN'}</span>
                                </span>
                            </div>
                            <div style="display: flex; flex-direction: column; text-align: right;">
                                <span style="font-size: 0.75rem; color: var(--base-muted-foreground); text-transform: uppercase;">Precio</span>
                                <span style="font-size: 1.2rem; font-weight: 800; color: var(--base-foreground);">$${producto.precio_venta}</span>
                            </div>
                        </div>
                    `;
                }

                if (typeof agregarProductoALista === 'function') {
                    agregarProductoALista(code.data);
                }
            })
            .catch(err => {
                feedbackText.textContent = err.message;
                feedbackText.style.color = '#ff3b3b';
            })
            .finally(() => {
                setTimeout(() => {
                    feedbackOverlay.style.display = 'none';
                    scanStatus.textContent = 'Esperando código QR...';
                    scanStatus.style.color = 'var(--base-foreground-muted)';

                    setTimeout(() => {
                        isProcessingCode = false;
                        requestAnimationFrame(scanQRCode);
                    }, 500);
                }, 2000);
            });
    } else {
        requestAnimationFrame(scanQRCode);
    }
}
