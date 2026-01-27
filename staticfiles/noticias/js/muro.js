// =========================
// CSRF
// =========================
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrftoken = getCookie("csrftoken");

// URLs que vienen desde el template (window.NEWS_URLS)
const URLS = window.NEWS_URLS || {};

// =========================
// SWIPER – GALERÍA
// =========================
let swiperInstance = null;

function openGalleryModal(postId, index) {
  fetch(`/noticias/media/${postId}/`, {
    headers: { "X-Requested-With": "XMLHttpRequest" }
  })
    .then(r => r.json())
    .then(data => {
      let content = "";
      (data.medios || []).forEach(m => {
        content += `
          <div class="swiper-slide d-flex justify-content-center align-items-center">
            ${
              m.tipo === "imagen"
                ? `<img src="${m.url}" class="img-fluid">`
                : `<video controls class="w-100"><source src="${m.url}"></video>`
            }
          </div>`;
      });

      const container = document.getElementById("swiperContent");
      if (!container) return;

      container.innerHTML = content;

      if (swiperInstance) {
        swiperInstance.destroy(true, true);
      }

      swiperInstance = new Swiper(".mySwiper", {
        loop: false,
        centeredSlides: true,
        spaceBetween: 20,
        pagination: {
          el: ".swiper-pagination",
          clickable: true
        },
        navigation: {
          nextEl: ".swiper-button-next",
          prevEl: ".swiper-button-prev"
        }
      });

      swiperInstance.slideTo(index || 0);

      const modal = new bootstrap.Modal(
        document.getElementById("modalSwiperGallery")
      );
      modal.show();
    });
}

// =========================
// COMENTARIOS – helpers
// =========================
function renderComentarioModal(com) {
  const tieneRespuestas = Array.isArray(com.respuestas) && com.respuestas.length > 0;

  return `
    <div class="fb-comment mb-2 p-2 border rounded" data-comment-id="${com.id}">
      <strong>${com.autor}:</strong> ${com.texto}<br>
      <small class="text-muted">${com.fecha}</small>

      <div class="d-flex align-items-center gap-3 mt-1 text-muted comment-actions">
        <!-- Like comentario -->
        <button class="btn btn-link btn-sm p-0 text-decoration-none btn-like-comment"
                data-comment-id="${com.id}">
          <i class="fas fa-thumbs-up me-1 ${com.liked ? "text-primary" : ""}"></i>
          <span class="comment-like-text">${com.liked ? "Te gusta" : "Me gusta"}</span>
        </button>

        <!-- contador likes -->
        <span class="comment-like-count" data-comment-id="${com.id}">
          ${com.total_likes} me gusta
        </span>

        <!-- 🔥 Botón responder SIEMPRE -->
        <button class="btn btn-link btn-sm p-0 text-decoration-none btn-reply-comment"
                data-comment-id="${com.id}">
          Responder
        </button>

        <!-- Toggle respuestas -->
        ${
          tieneRespuestas
            ? `<a href="#" class="text-muted small ms-2 toggle-respuestas"
                 data-comment-id="${com.id}">
                 Ver ${com.respuestas.length} respuesta${com.respuestas.length !== 1 ? "s" : ""}
               </a>`
            : ""
        }
      </div>

      <!-- Contenedor de respuestas -->
      <div class="respuesta-container mt-2 ms-4 d-none">
        ${
          tieneRespuestas
            ? com.respuestas.map(r => renderComentarioModal(r)).join("")
            : ""
        }
      </div>
    </div>
  `;
}

function cargarComentariosEnModal(postId, keepOpen = false) {
  const urlBase = (URLS.listaComentarios || "").replace("/0/", `/${postId}/`);

  fetch(urlBase, { headers: { "X-Requested-With": "XMLHttpRequest" } })
    .then(r => r.json())
    .then(data => {
      const comentarios = data.comentarios || [];
      const body = document.getElementById("commentsModalBody");
      if (!body) return;

      // reconstruir html
      let html = comentarios.length
        ? comentarios.map(c => renderComentarioModal(c)).join("")
        : "<p class='text-muted mb-0'>Aún no hay comentarios.</p>";

      body.innerHTML = html;

      // ⛔ NO volver a abrir el modal si ya estaba abierto
      if (!keepOpen) {
        const modal = new bootstrap.Modal(document.getElementById("commentsModal"));
        modal.show();
      }
    });
}



// =========================
// INICIALIZACIÓN
// =========================
let activeReplyFormParent = null;

document.addEventListener("DOMContentLoaded", function () {
  // Tooltips
  const tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  tooltipTriggerList.forEach(t => new bootstrap.Tooltip(t));

  // Listener submit de edición
  const formEditar = document.getElementById("formEditarPost");
  if (formEditar) {
    formEditar.addEventListener("submit", onSubmitEditarPost);
  }
});


// =========================
// CLICK GLOBAL
// =========================
document.addEventListener("click", function (e) {
  // 1) Like a post
  // 🌟 Enviar comentario (nuevo)
  const btnSendComment = e.target.closest(".btn-enviar-comentario");
  if (btnSendComment) {

    const postId = btnSendComment.dataset.postId;
    const input = document.querySelector(`#comentario-input-${postId}`);
    const texto = (input?.value || "").trim();
    if (!texto) return;

    const url = (URLS.agregarComentario || "").replace("/0/", `/${postId}/`);

    fetch(url, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrftoken,
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: new URLSearchParams({ texto })
    })
      .then(res => {
        if (res.status === 401) {
          Swal.fire({
            icon: "warning",
            title: "Inicia sesión",
            text: "Debes tener una cuenta para comentar.",
            confirmButtonText: "Iniciar sesión"
          }).then(() => {
            window.location.href = "/login/";  // URL real de tu login
          });
          return;
        }
        return res.json();
      })
      .then(data => {
        if (!data || !data.success) return;

        // 🔥 limpiar input
        input.value = "";

        // 🔥 refrescar comentarios automáticamente
        cargarComentariosEnModal(postId);
      });

    return;
  }


  const btnLike = e.target.closest(".btn-like");
  if (btnLike) {
    const postId = btnLike.dataset.postId;
    const urlBase = (URLS.toggleLike || "").replace("/0/", `/${postId}/`);

    fetch(urlBase, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrftoken,
        "X-Requested-With": "XMLHttpRequest"
      }
    })
      .then(r => r.json())
      .then(data => {
        const icon = btnLike.querySelector("i");
        const text = btnLike.querySelector(".like-text");
        const count = document.querySelector(
          `.like-count[data-post-id="${postId}"]`
        );

        if (data.liked) {
          icon.classList.add("text-primary");
          text.textContent = "Te gusta";
        } else {
          icon.classList.remove("text-primary");
          text.textContent = "Me gusta";
        }

        if (count) {
          count.textContent = `${data.total_likes} Me gusta`;
        }
      });

    return;
  }

  // 2) Lista de likes
  const likeCount = e.target.closest(".like-count");
  if (likeCount) {
    const postId = likeCount.dataset.postId;
    const urlBase = (URLS.listaLikes || "").replace("/0/", `/${postId}/`);

    fetch(urlBase, { headers: { "X-Requested-With": "XMLHttpRequest" } })
      .then(r => r.json())
      .then(data => {
        const body = document.getElementById("likesModalBody");
        if (!body) return;

        let html = data.likes.length
          ? `<ul class="list-group">` +
            data.likes.map(u => `
                <li class="list-group-item">
                  <i class="fas fa-user-circle text-primary me-2"></i>
                  ${u.nombre}
                </li>`).join("") +
            `</ul>`
          : `<p class="mb-0">Aún no hay Me gusta.</p>`;

        body.innerHTML = html;

        const modal = new bootstrap.Modal(
          document.getElementById("likesModal")
        );
        modal.show();

        document.querySelectorAll(".tooltip").forEach(t => t.remove());
      });

    return;
  }

  // 3) Abrir modal de comentarios
  const commentCount = e.target.closest(".comment-count");
  if (commentCount) {
    cargarComentariosEnModal(commentCount.dataset.postId);
    return;
  }

  const verTodos = e.target.closest(".ver-todos-comentarios");
  if (verTodos) {
    cargarComentariosEnModal(verTodos.dataset.postId);
    return;
  }

  // 4) Like a comentario
  const btnLikeComment = e.target.closest(".btn-like-comment");
  if (btnLikeComment) {
    const commentId = btnLikeComment.dataset.commentId;
    const urlBase = (URLS.toggleLikeComentario || "").replace(
      "/0/",
      `/${commentId}/`
    );

    fetch(urlBase, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrftoken,
        "X-Requested-With": "XMLHttpRequest"
      }
    })
      .then(r => r.json())
      .then(data => {
        const icon = btnLikeComment.querySelector("i");
        const text = btnLikeComment.querySelector(".comment-like-text");
        const counts = document.querySelectorAll(
          `.comment-like-count[data-comment-id="${commentId}"]`
        );

        if (data.liked) {
          icon.classList.add("text-primary");
          text.textContent = "Te gusta";
        } else {
          icon.classList.remove("text-primary");
          text.textContent = "Me gusta";
        }

        counts.forEach(c => (c.textContent = `${data.total_likes} me gusta`));
      });

    return;
  }

// 5) Mostrar / ocultar respuestas (feed + modal)
const toggleResp = e.target.closest(".toggle-respuestas");
if (toggleResp) {
  e.preventDefault();
  const commentId = toggleResp.dataset.commentId;

  // Buscar comentario tanto en modal como en feed
  let parent =
    document.querySelector(`#commentsModalBody .fb-comment[data-comment-id="${commentId}"]`)
    || document.querySelector(`.fb-comment[data-comment-id="${commentId}"]`);

  if (!parent) return;

  const container = parent.querySelector(".respuesta-container");
  if (!container) return;

  const hidden = container.classList.toggle("d-none");

  if (hidden) {
    const total = container.querySelectorAll(".fb-comment").length;
    toggleResp.textContent =
      total === 1 ? "Ver 1 respuesta" : `Ver ${total} respuestas`;
  } else {
    toggleResp.textContent = "Ocultar respuestas";
  }

  return;
}


  // 6) Responder comentario
  const btnReply = e.target.closest(".btn-reply-comment");
if (btnReply) {

  const commentId = btnReply.dataset.commentId;

    // 1) Buscar dentro del MODAL (tiene prioridad)
    const modalBody = document.getElementById("commentsModalBody");
    let parent = null;

    if (modalBody) {
    parent = modalBody.querySelector(
        `.fb-comment[data-comment-id="${commentId}"]`
    );
    }

    // 2) Si NO está en el modal, buscar en el FEED
    if (!parent) {
    parent = document.querySelector(
        `.fb-comment[data-comment-id="${commentId}"]`
    );
    }

    if (!parent) return;


  // cerrar si ya existe
  if (activeReplyFormParent && activeReplyFormParent !== parent) {
    const old = activeReplyFormParent.querySelector(".reply-form");
    if (old) old.remove();
  }

  const existing = parent.querySelector(".reply-form");
  if (existing) {
    existing.remove();
    activeReplyFormParent = null;
    return;
  }

  parent.insertAdjacentHTML(
    "beforeend",
    `
<form class="reply-form mt-2">
  <div class="input-group input-group-sm">
    <input type="text"
           name="texto"
           class="form-control reply-input"
           placeholder="Escribe una respuesta...">
    <button class="btn btn-primary" type="submit">Responder</button>
  </div>
</form>`
  );

  activeReplyFormParent = parent;

  const form = parent.querySelector(".reply-form");

      // 🔥 AUTOFOCUS REAL
  const input = parent.querySelector(".reply-input");
  if (input) {
    setTimeout(() => input.focus(), 30);
  }


  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    const texto = form.querySelector("input").value.trim();
    if (!texto) return;

    const url = URLS.responderComentario.replace("/0/", `/${commentId}/`);

    fetch(url, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrftoken,
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: new URLSearchParams({ texto })
    })
      .then(r => r.json()) // 🔥 Necesario
      .then(data => {

        // refrescar modal si está abierto
        const modal = bootstrap.Modal.getInstance(
          document.getElementById("commentsModal")
        );

        if (modal) {
          cargarComentariosEnModal(data.post_id, true);
        } else {
          // refrescar lista del feed
          const urlFeed = URLS.listaComentarios.replace("/0/", `/${data.post_id}/`);
          fetch(urlFeed, { headers: { "X-Requested-With": "XMLHttpRequest" } })
            .then(r => r.json())
            .then(res => {
              const cont = document.querySelector(
                `.comentarios[data-post-id="${data.post_id}"]`
              );
              if (cont) {
                cont.innerHTML = res.comentarios
                  .map(c => renderComentarioModal(c))
                  .join("");
              }
            });
        }

        form.remove();
        activeReplyFormParent = null;
      });
  });

  return;
}


  // 7) Ver más / ver menos texto post
  const verMas = e.target.closest(".ver-mas-btn");
  if (verMas) {
    const id = verMas.dataset.postId;
    const texto = document.getElementById("post-text-" + id);
    if (!texto) return;

    texto.classList.add("expanded");
    verMas.textContent = "Ver menos";
    verMas.classList.add("ver-menos-btn");
    verMas.classList.remove("ver-mas-btn");
    return;
  }

  const verMenos = e.target.closest(".ver-menos-btn");
  if (verMenos) {
    const id = verMenos.dataset.postId;
    const texto = document.getElementById("post-text-" + id);
    if (!texto) return;

    texto.classList.remove("expanded");
    verMenos.textContent = "Ver más…";
    verMenos.classList.add("ver-mas-btn");
    verMenos.classList.remove("ver-menos-btn");
    return;
  }

  // 8) Abrir modal edición
  const editarBtn = e.target.closest(".btn-editar-post");
  if (editarBtn) {
    const postId = editarBtn.dataset.postId;
    const contenido = editarBtn.dataset.postContenido || "";
    const txt = document.getElementById("editarContenido");
    const form = document.getElementById("formEditarPost");
    if (!txt || !form) return;

    txt.value = contenido;
    form.dataset.postId = postId;

    fetch(`/noticias/media/${postId}/`, {
      headers: { "X-Requested-With": "XMLHttpRequest" }
    })
      .then(r => r.json())
      .then(data => {
        const cont = document.getElementById("editarMediaActual");
        if (!cont) return;
        cont.innerHTML = "";

        (data.medios || []).forEach(m => {
            cont.innerHTML += `
            <div class="col-4">
                <div class="media-edit-item">

                    <input type="checkbox"
                            class="media-edit-check eliminar-media-checkbox"
                            value="${m.id}"
                            name="eliminar_media[]">

                    ${
                        m.tipo === "imagen"
                        ? `<img src="${m.url}" alt="">`
                        : `<video src="${m.url}" muted></video>`
                    }

                </div>
            </div>`;

        });
      });

    const modal = new bootstrap.Modal(
      document.getElementById("modalEditarPost")
    );
    modal.show();
    return;
  }

  // 9) Eliminar publicación
// 9) Eliminar publicación (con SweetAlert)
const eliminarBtn = e.target.closest(".btn-eliminar-post");
if (eliminarBtn) {
  const postId = eliminarBtn.dataset.postId;

  Swal.fire({
    title: "¿Eliminar publicación?",
    text: "Esta acción no se puede deshacer.",
    icon: "warning",
    showCancelButton: true,
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
    confirmButtonColor: "#e11d48",  // rojo bonito
    cancelButtonColor: "#6b7280"
  }).then(result => {
    if (!result.isConfirmed) return;

    fetch(`/noticias/eliminar/${postId}/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrftoken,
        "X-Requested-With": "XMLHttpRequest"
      }
    })
      .then(r => r.json())
      .then(data => {
        if (data.success) {
          const card = document.getElementById("post-" + postId);
          if (card) card.remove();

          Swal.fire({
            icon: "success",
            title: "Publicación eliminada",
            timer: 1500,
            showConfirmButton: false
          });
        } else {
          Swal.fire({
            icon: "error",
            title: "Error",
            text: "No se pudo eliminar la publicación."
          });
        }
      })
      .catch(() => {
        Swal.fire({
          icon: "error",
          title: "Error",
          text: "Ocurrió un problema al eliminar."
        });
      });
  });

  return;
}


  // 10) Clic en miniatura de galería (abrir Swiper)
  const galleryItem = e.target.closest(".fb-gallery-item");
  if (galleryItem) {
    const postId = galleryItem.dataset.postId;
    const index = parseInt(galleryItem.dataset.index || "0", 10);
    openGalleryModal(postId, index);
    return;
  }
});

// =========================
// SUBMIT EDICIÓN POST
// =========================
function onSubmitEditarPost(e) {
  e.preventDefault();
  const form = e.target;
  const postId = form.dataset.postId;
  if (!postId) return;

  let formData = new FormData();
  formData.append("contenido", document.getElementById("editarContenido").value);

  document
    .querySelectorAll(".eliminar-media-checkbox:checked")
    .forEach(chk => formData.append("eliminar_media[]", chk.value));

  const nuevos = document.getElementById("nuevoMedia").files;
  for (let i = 0; i < nuevos.length; i++) {
    formData.append("nuevo_media", nuevos[i]);
  }

  fetch(`/noticias/editar/${postId}/`, {
    method: "POST",
    headers: { "X-CSRFToken": csrftoken },
    body: formData
  })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        const texto = document.querySelector(`#post-${postId} .post-text`);
        if (texto) {
          texto.innerHTML = data.html;
        }

        const modalEl = document.getElementById("modalEditarPost");
        bootstrap.Modal.getInstance(modalEl).hide();

        // recargar solo para refrescar mosaico
        window.location.reload();
      }
    });

}


