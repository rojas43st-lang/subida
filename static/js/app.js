(() => {
  "use strict";
  const input = document.getElementById("archivos");
  const seleccion = document.getElementById("seleccion");
  const dropZone = document.querySelector(".drop-zone");
  const formulario = document.getElementById("formularioSubida");
  const busqueda = document.getElementById("busqueda");
  const botonTema = document.getElementById("botonTema");
  const iconoTema = document.getElementById("iconoTema");

  if (input && seleccion) {
    input.addEventListener("change", () => {
      const archivos = Array.from(input.files || []);
      if (!archivos.length) {
        seleccion.textContent = "No has seleccionado archivos.";
        return;
      }
      const total = archivos.reduce((suma, archivo) => suma + archivo.size, 0);
      seleccion.innerHTML = `<strong>${archivos.length}</strong> archivo(s) seleccionado(s) · ${(total / 1024 / 1024).toFixed(2)} MB`;
      const lista = document.createElement("div");
      lista.className = "mt-2";
      archivos.slice(0, 5).forEach(archivo => {
        const linea = document.createElement("div");
        linea.className = "text-truncate";
        linea.textContent = "• " + archivo.name;
        lista.appendChild(linea);
      });
      if (archivos.length > 5) {
        const extra = document.createElement("div");
        extra.textContent = `y ${archivos.length - 5} archivo(s) más`;
        lista.appendChild(extra);
      }
      seleccion.appendChild(lista);
    });

    ["dragenter", "dragover"].forEach(evento => dropZone?.addEventListener(evento, e => {
      e.preventDefault(); dropZone.classList.add("dragging");
    }));
    ["dragleave", "drop"].forEach(evento => dropZone?.addEventListener(evento, e => {
      e.preventDefault(); dropZone.classList.remove("dragging");
    }));
    dropZone?.addEventListener("drop", e => {
      if (e.dataTransfer?.files?.length) {
        input.files = e.dataTransfer.files;
        input.dispatchEvent(new Event("change"));
      }
    });
    formulario?.addEventListener("submit", e => {
      if (!input.files.length) {
        e.preventDefault();
        seleccion.textContent = "Selecciona al menos un archivo antes de subir.";
      } else if (Array.from(input.files).some(f => f.size > 20 * 1024 * 1024)) {
        e.preventDefault();
        seleccion.textContent = "Uno o más archivos superan el límite de 20 MB.";
      }
    });
  }

  if (busqueda) {
    busqueda.addEventListener("input", () => {
      const texto = busqueda.value.trim().toLocaleLowerCase("es");
      const filas = Array.from(document.querySelectorAll(".fila-archivo"));
      let visibles = 0;
      filas.forEach(fila => {
        const coincide = (fila.dataset.nombre || "").includes(texto);
        fila.classList.toggle("d-none", !coincide);
        if (coincide) visibles++;
      });
      document.getElementById("sinResultados")?.classList.toggle("d-none", visibles > 0 || filas.length === 0);
    });
  }

  function aplicarTema(tema) {
    document.documentElement.setAttribute("data-bs-theme", tema);
    if (iconoTema) iconoTema.className = tema === "dark" ? "bi bi-sun-fill" : "bi bi-moon-stars-fill";
    try { localStorage.setItem("subefacil-tema", tema); } catch (_) {}
  }
  let guardado = null;
  try { guardado = localStorage.getItem("subefacil-tema"); } catch (_) {}
  aplicarTema(guardado || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"));
  botonTema?.addEventListener("click", () => {
    aplicarTema(document.documentElement.getAttribute("data-bs-theme") === "dark" ? "light" : "dark");
  });
})();
