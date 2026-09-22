/* ============================================================
   Luca Castello - comportamiento del sitio (sin librerias)
   ============================================================ */
(function () {
  "use strict";

  /* ---------- videos ----------
     Cada video es una caratula (miniatura). Al hacer click se cambia por el
     reproductor de YouTube en el mismo lugar. Si ya habia otro sonando, ese
     vuelve a su caratula: nunca hay mas de un reproductor cargado. */
  var actual = null;

  function restaurar(caja) {
    var f = caja.querySelector("iframe, video");
    if (f) { if (f.pause) f.pause(); f.remove(); }
    caja.classList.remove("activo");
  }

  function reproducir(caja) {
    if (caja.classList.contains("activo")) return;
    if (actual && actual !== caja) restaurar(actual);
    var el;
    if (caja.dataset.mp4) {
      // video alojado en el sitio: reproductor nativo del navegador
      el = document.createElement("video");
      el.src = caja.dataset.mp4;
      el.controls = true;
      el.autoplay = true;
      el.playsInline = true;
    } else {
      el = document.createElement("iframe");
      el.src = "https://www.youtube-nocookie.com/embed/" + caja.dataset.youtube +
        "?autoplay=1&rel=0&modestbranding=1&playsinline=1";
      el.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";
      el.allowFullscreen = true;
    }
    el.title = caja.dataset.titulo || "Video";
    caja.appendChild(el);
    caja.classList.add("activo");
    actual = caja;
  }

  function esVideo(v) { return v && (v.dataset.youtube || v.dataset.mp4); }

  document.addEventListener("click", function (e) {
    var v = e.target.closest(".video");
    if (esVideo(v)) reproducir(v);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Enter" && e.key !== " ") return;
    var v = e.target.closest(".video");
    if (!esVideo(v) || v.classList.contains("activo")) return;
    e.preventDefault();
    reproducir(v);
  });

  /* ---------- slideshow de la portada (desliza como el original) ---------- */
  var pista = document.querySelector(".portada__pista");
  var puntos = document.querySelectorAll(".portada__puntos button");
  if (pista && pista.children.length > 1) {
    var total = pista.children.length, i = 0, reloj = null;
    var ir = function (n) {
      i = (n + total) % total;
      pista.style.transform = "translateX(" + (-100 * i) + "%)";
      for (var k = 0; k < total; k++) pista.children[k].classList.toggle("activo", k === i);
      puntos.forEach(function (b, k) { b.classList.toggle("activo", k === i); });
    };
    var arrancar = function () {
      clearInterval(reloj);
      reloj = setInterval(function () { ir(i + 1); }, 4000);
    };
    puntos.forEach(function (b, k) { b.addEventListener("click", function () { ir(k); arrancar(); }); });
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) clearInterval(reloj); else arrancar();
    });
    ir(0);
    arrancar();
  }

  /* ---------- las obras van apareciendo a medida que se scrollea ---------- */
  var items = document.querySelectorAll(".revela, .revela-movil");
  if ("IntersectionObserver" in window) {
    var obs = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("visible"); obs.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -60px 0px", threshold: 0.05 });
    items.forEach(function (el) { obs.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add("visible"); });
  }
})();
