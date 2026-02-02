
    $(document).ready(function () {

          // Filtro simple por título
 // --- Filtro en vivo como en álbumes, pero para .list-group-item ---
        (function () {
            const input = document.getElementById('searchInput');
            if (!input) return;

            // Función para normalizar (quita acentos y pasa a minúsculas)
            const norm = (s) => (s || '')
            .toString()
            .toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '');

            input.addEventListener('input', () => {
            const q = norm(input.value);
            document.querySelectorAll('.list-group-item').forEach(item => {
                // 1) intenta con data-title; 2) fallback: texto visible
                const title = item.dataset.title
                ? norm(item.dataset.title)
                : norm(item.textContent || '');

                item.style.display = title.includes(q) ? '' : 'none';
            });
            });
        })();

        $(".editar-btn").click(function() {
        var marchaID = $(this).data("marchaid");
        if (!marchaID) { console.error("Error: Marcha ID no definido."); return; }
        var formulario = "{% url 'aplicacion:editar_marcha' 0 %}".replace("0", marchaID);

        Swal.fire({
            title: 'Editar Marcha Fúnebre',
            html: `<iframe src="${formulario}" width="100%" height="500vh" frameborder="0" style="max-width: 100%;"></iframe>`,
            showCloseButton: true,
            showConfirmButton: false,
            customClass: { container: 'swal-container', popup: 'swal-popup my-custom-modal-class' },
            didClose: () => { location.reload(); },
        });

        window.addEventListener('message', function (event) {
            if (event.data === 'closeModal') { Swal.close(); }
        });

        return false;
    });

    $(".btn-delete").click(function() {
        var marchaID = $(this).data("marchaid");
        if (!marchaID) { console.error("Error: Marcha ID no definido."); return; }
        var formulario = "{% url 'aplicacion:eliminar_marcha' 0 %}".replace("0", marchaID);

        Swal.fire({
            title: 'Eliminar Marcha Fúnebre',
            html: `<iframe src="${formulario}" width="100%" height="500vh" frameborder="0" style="max-width: 100%;"></iframe>`,
            showCloseButton: true,
            showConfirmButton: false,
            customClass: { container: 'swal-container', popup: 'swal-popup my-custom-modal-class' },
            didClose: () => { location.reload(); },
        });

        window.addEventListener('message', function (event) {
            if (event.data === 'closeModal') { Swal.close(); }
        });

        return false;
    });


});

    let currentMarchaIndex = -1;
    let marchasLista = [];
    let modoRepetir = 0; // 0 = off, 1 = repeat one, 2 = repeat all
    let modoAleatorio = false;

    function setupMediaSession({ titulo, descripcion, imagen }) {
    if (!("mediaSession" in navigator)) return;

    // Metadata: lo que se ve en bloqueo / notificación
    navigator.mediaSession.metadata = new MediaMetadata({
        title: titulo || "Marcha fúnebre",
        artist: descripcion || " ",
        album: "Marchas Fúnebres",
        artwork: [
        { src: imagen, sizes: "512x512", type: "image/png" },
        { src: imagen, sizes: "256x256", type: "image/png" },
        { src: imagen, sizes: "128x128", type: "image/png" }
        ]
    });

    const player = document.getElementById("audioPlayer");
    if (!player) return;

    // Acciones (Android suele mostrar prev/next; iOS Safari a veces NO)
    try {
        navigator.mediaSession.setActionHandler("play", () => player.play());
        navigator.mediaSession.setActionHandler("pause", () => player.pause());

        navigator.mediaSession.setActionHandler("previoustrack", () => retrocederMarcha());
        navigator.mediaSession.setActionHandler("nexttrack", () => siguienteMarcha());

        // Opcionales (algunos Android muestran saltos)
        navigator.mediaSession.setActionHandler("seekbackward", (details) => {
        const s = details?.seekOffset ?? 10;
        player.currentTime = Math.max(0, player.currentTime - s);
        });
        navigator.mediaSession.setActionHandler("seekforward", (details) => {
        const s = details?.seekOffset ?? 10;
        player.currentTime = Math.min(player.duration || player.currentTime + s, player.currentTime + s);
        });
    } catch (e) {
        // algunos navegadores lanzan error si no soportan esa action
    }
    }


    document.addEventListener('DOMContentLoaded', function () {
        marchasLista = Array.from(document.querySelectorAll('.list-group-item'));
    });

    function reproducirMarcha(audioUrl, titulo, descripcion, imagen, marchaId) {
        const player = document.getElementById('audioPlayer');
        const source = document.getElementById('audioSource');
        const card = document.getElementById('reproductorCard');
        const portada = document.getElementById('portadaMarcha');
  

        source.src = audioUrl;
        player.load();
        player.play();

        setupMediaSession({ titulo, descripcion, imagen });

        player.onended = () => {
        if (modoRepetir === 2) {
            // Repetir pista actual
            player.currentTime = 0;
            player.play();
        } else if (modoRepetir === 1 && modoAleatorio) {
            // Repetir lista en modo aleatorio
            let siguiente;
            do {
                siguiente = Math.floor(Math.random() * marchasLista.length);
            } while (siguiente === currentMarchaIndex && marchasLista.length > 1);
            reproducirDesdeElemento(marchasLista[siguiente]);
        } else if (modoRepetir === 1 && !modoAleatorio) {
            // Repetir lista en orden
            if (currentMarchaIndex < marchasLista.length - 1) {
                reproducirDesdeElemento(marchasLista[currentMarchaIndex + 1]);
            } else {
                reproducirDesdeElemento(marchasLista[0]); // volver al inicio
            }
        } else if (modoRepetir === 0 && modoAleatorio) {
            // Aleatorio sin repetir lista (se detiene al llegar al final)
            if (currentMarchaIndex < marchasLista.length - 1) {
                let siguiente;
                do {
                    siguiente = Math.floor(Math.random() * marchasLista.length);
                } while (siguiente === currentMarchaIndex && marchasLista.length > 1);
                reproducirDesdeElemento(marchasLista[siguiente]);
            }
            // Si ya no hay más, no hace nada (detiene)
        } else if (modoRepetir === 0 && !modoAleatorio) {
            // Reproducción normal
            if (currentMarchaIndex < marchasLista.length - 1) {
                reproducirDesdeElemento(marchasLista[currentMarchaIndex + 1]);
            }
        }
        console.log("Reproduciendo:", audioUrl);

        };

        document.getElementById('tituloMarcha').innerText = titulo;
        document.getElementById('descripcionMarcha').innerText = descripcion;
        portada.src = imagen;
        card.style.display = 'flex';

        window.marchaActualId = marchaId;

        // Marcar favorita en reproductor
        // Marcar favorita en reproductor (SOLO si está logueado)
        const icono = document.getElementById('iconoFavorito');

        if (!USER_AUTH) {
        // invitado: no consultes al backend, solo deja el corazón "apagado"
        icono?.classList.remove('text-danger');
        } else {
        fetch(`/marchas/es-favorita/${marchaId}/`)
            .then(res => res.json())
            .then(data => {
            if (data.favorita) icono.classList.add('text-danger');
            else icono.classList.remove('text-danger');
            })
            .catch(() => {
            // si falla, no rompemos reproducción
            icono?.classList.remove('text-danger');
            });
        }


        marchasLista.forEach(item => item.classList.remove('active-marcha'));
        const marchaActiva = document.getElementById(`marcha_${marchaId}`);
        if (marchaActiva) {
            marchaActiva.classList.add('active-marcha');
        }

        currentMarchaIndex = marchasLista.findIndex(item => item.id === `marcha_${marchaId}`);

    }

    function detenerMarcha() {
        const player = document.getElementById('audioPlayer');
        player.pause();
        player.currentTime = 0;
    }

    function siguienteMarcha(fromRepeat = false) {
    if (modoAleatorio) {
        let aleatorioIndex;
        do {
            aleatorioIndex = Math.floor(Math.random() * marchasLista.length);
        } while (aleatorioIndex === currentMarchaIndex && marchasLista.length > 1);

        reproducirDesdeElemento(marchasLista[aleatorioIndex]);
    } else if (currentMarchaIndex < marchasLista.length - 1) {
        reproducirDesdeElemento(marchasLista[currentMarchaIndex + 1]);
    } else if (fromRepeat && modoRepetir === 2) {
        // Si llegó al final y el modo es repetir lista completa
        reproducirDesdeElemento(marchasLista[0]);
    }
}

function retrocederMarcha() {
    if (currentMarchaIndex > 0) {
        reproducirDesdeElemento(marchasLista[currentMarchaIndex - 1]);
    }
}

function reproducirDesdeElemento(elemento) {
    const btn = elemento.querySelector('button[onclick^="reproducirMarcha"]');
    if (btn) btn.click();
}



    document.getElementById('favoritoBtnReproductor').addEventListener('click', () => {

        
        if (!USER_AUTH) {
            Swal.fire("Inicia sesión", "Debes iniciar sesión para guardar favoritas.", "info");
            return;
        }

        const marchaId = window.marchaActualId;
        if (!marchaId) return;

        fetch(`/marchas/favorito/toggle/${marchaId}/`)
            .then(response => response.json())
            .then(data => {
                const icono = document.getElementById('iconoFavorito');
                const iconoLista = document.querySelector(`#favoritoBtnLista_${marchaId} i`);

                if (data.estado === 'agregado') {
                    icono.classList.add('text-danger');
                    if (iconoLista) iconoLista.classList.add('text-danger');
                } else {
                    icono.classList.remove('text-danger');
                    if (iconoLista) iconoLista.classList.remove('text-danger');
                }
            });
    });

    function toggleFavoritoLista(marchaId) {
        
        if (!USER_AUTH) {
            Swal.fire("Inicia sesión", "Debes iniciar sesión para guardar favoritas.", "info");
            return;
        }

        fetch(`/marchas/favorito/toggle/${marchaId}/`)
            .then(response => response.json())
            .then(data => {
                const icono = document.querySelector(`#favoritoBtnLista_${marchaId} i`);
                const iconoReproductor = document.getElementById('iconoFavorito');

                if (data.estado === 'agregado') {
                    icono.classList.add('text-danger');
                    if (marchaId == window.marchaActualId) {
                        iconoReproductor.classList.add('text-danger');
                    }
                } else {
                    icono.classList.remove('text-danger');
                    if (marchaId == window.marchaActualId) {
                        iconoReproductor.classList.remove('text-danger');
                    }
                }
            });
    }

    function toggleRepetir() {
    modoRepetir = (modoRepetir + 1) % 3;

    const icono = document.getElementById('iconoRepetir');
    const badge = document.getElementById('badgeRepetir');

    switch (modoRepetir) {
        case 0: // Desactivado
            icono.classList.add('fa-inactive');
            badge.style.display = 'none';
            icono.title = 'Repetir desactivado';
            break;

        case 1: // Repetir toda la lista
            icono.classList.remove('fa-inactive');
            badge.style.display = 'none';
            icono.title = 'Repetir lista completa';
            break;

        case 2: // Repetir una marcha
            icono.classList.remove('fa-inactive');
            badge.style.display = 'block';
            icono.title = 'Repetir esta marcha';
            break;
    }
}

function toggleAleatorio() {
    modoAleatorio = !modoAleatorio;
    const icono = document.getElementById('iconoAleatorio');

    if (modoAleatorio) {
        icono.classList.remove('fa-inactive');
        icono.title = 'Modo aleatorio activado';
    } else {
        icono.classList.add('fa-inactive');
        icono.title = 'Modo aleatorio desactivado';
    }
}

// Minimizar / restaurar player
// Minimizar / restaurar hacia la IZQUIERDA
const btnMin = document.getElementById('minimizarPlayer');
const playerCard = document.getElementById('reproductorCard');

btnMin?.addEventListener('click', () => {
  const icon = btnMin.querySelector('i');
  const isMin = playerCard.classList.toggle('minimized-left');

  // Cuando queda minimizado, usamos padding compacto
  if (isMin){
    document.documentElement.classList.add('player-open-compact');
    document.body.classList.add('player-open-compact');
    icon.classList.remove('fa-chevron-left');
    icon.classList.add('fa-chevron-right');   // indica que vuelve a abrirse
    btnMin.title = 'Expandir';
    btnMin.setAttribute('aria-label','Expandir reproductor');
  }else{
    document.documentElement.classList.remove('player-open-compact');
    document.body.classList.remove('player-open-compact');
    icon.classList.remove('fa-chevron-right');
    icon.classList.add('fa-chevron-left');    // indica que puede minimizarse
    btnMin.title = 'Minimizar';
    btnMin.setAttribute('aria-label','Minimizar reproductor');
  }
});

(function attachPositionState(){
  const player = document.getElementById("audioPlayer");
  if (!player || !("mediaSession" in navigator)) return;

  player.addEventListener("timeupdate", () => {
    if (!player.duration) return;
    try {
      navigator.mediaSession.setPositionState({
        duration: player.duration,
        playbackRate: player.playbackRate,
        position: player.currentTime
      });
    } catch (e) {}
  });
})();


