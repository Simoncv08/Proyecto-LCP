document.addEventListener("DOMContentLoaded", function () {
    const eventoSelect = document.querySelector('select[name="evento"]');
    const contenedor = document.getElementById("productos");
    const totalInput = document.getElementById("total");
    const precioBaseMsg = document.getElementById("precio-base");

    if (!eventoSelect || !contenedor) return;

    function calcularTotal() {
        let total = 0;
        document.querySelectorAll("[data-precio]").forEach(input => {
            const precio = parseInt(input.dataset.precio);
            const cantidad = parseInt(input.value) || 0;
            total += precio * cantidad;
        });
        if (totalInput) {
            totalInput.value = "$ " + total.toLocaleString("es-CO");
        }
    }

    eventoSelect.addEventListener("change", function () {
        const eventoId = this.value;
        fetch(`/productos/${eventoId}/`)
            .then(res => res.json())
            .then(data => {
                let html = "";
                if (data.productos.length === 0) {
                    contenedor.innerHTML = "";
                    precioBaseMsg.style.display = "block";
                    totalInput.value = "$ " + data.precio_base.toLocaleString("es-CO");
                } else {
                    precioBaseMsg.style.display = "none";
                    data.productos.forEach(p => {
                        html += `
                            <div class="mb-2">
                                <div class="d-flex justify-content-between align-items-center">
                                    <span>${p.nombre} ($${p.precio.toLocaleString("es-CO")})</span>
                                    <input 
                                        type="number" min="0" value="0"
                                        data-precio="${p.precio}"
                                        name="producto_${p.id}"
                                        class="form-control w-25 cantidad"
                                    >
                                </div>
                            </div>`;
                    });
                    contenedor.innerHTML = html;
                    document.querySelectorAll(".cantidad").forEach(input => {
                        input.addEventListener("input", calcularTotal);
                    });
                    calcularTotal();
                }
            });
    });
});

let contador = 0;

function agregarProducto() {
    const container = document.getElementById("productos-container");
    const html = `
        <div class="row mb-2 align-items-center producto-item" id="producto_${contador}">
            <div class="col">
                <input type="text" name="producto_nombre_${contador}" 
                    class="form-control nombre-producto" placeholder="Nombre del producto">
            </div>
            <div class="col">
                <input type="number" name="producto_precio_${contador}" 
                    class="form-control precio-producto" placeholder="Precio" min="0">
            </div>
            <div class="col-auto">
                <button type="button" class="btn btn-danger btn-sm"
                    onclick="eliminarProducto(${contador})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>`;
    container.insertAdjacentHTML("beforeend", html);
    contador++;
}

function eliminarProducto(id) {
    const item = document.getElementById(`producto_${id}`);
    if (item) item.remove();
}

document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", function (e) {
            let valido = true;
            document.querySelectorAll(".producto-item").forEach(item => {
                const nombre = item.querySelector(".nombre-producto").value.trim();
                const precio = item.querySelector(".precio-producto").value.trim();
                if ((nombre && !precio) || (!nombre && precio)) {
                    valido = false;
                    item.classList.add("border", "border-danger", "p-2");
                } else {
                    item.classList.remove("border", "border-danger", "p-2");
                }
            });
            if (!valido) {
                e.preventDefault();
                alert("Completa correctamente los productos (nombre y precio).");
            }
        });
    }
});


document.addEventListener("DOMContentLoaded", function () {
    const filtroGrado   = document.getElementById("filtro-grado");
    const filtroSeccion = document.getElementById("filtro-seccion");
    const selectorEstudiante = document.getElementById("id_estudiante");

    // Solo corre en páginas que tengan el selector de estudiante
    if (!filtroGrado || !filtroSeccion || !selectorEstudiante) return;

    function cargarEstudiantes() {
        const grado   = filtroGrado.value;
        const seccion = filtroSeccion.value;

        const params = new URLSearchParams();
        if (grado)   params.append("grado", grado);
        if (seccion) params.append("seccion", seccion);

        fetch(`/api/estudiantes/?${params}`)
            .then(r => r.json())
            .then(data => {
                selectorEstudiante.innerHTML =
                    '<option value="">-- Selecciona un estudiante --</option>';

                data.forEach(e => {
                    const opt = document.createElement("option");
                    opt.value = e.id;
                    opt.textContent = `${e.nombre} (${e.grado}${e.seccion})`;
                    selectorEstudiante.appendChild(opt);
                });
            });
    }

    filtroGrado.addEventListener("change", cargarEstudiantes);
    filtroSeccion.addEventListener("change", cargarEstudiantes);
});


document.addEventListener("DOMContentLoaded", function () {
    const filtroGrado    = document.getElementById("filtro-grado");
    const filtroSeccion  = document.getElementById("filtro-seccion");
    const selectorEstudiante = document.getElementById("id_estudiante");

    if (!filtroGrado || !filtroSeccion || !selectorEstudiante) return;

    function cargarEstudiantes() {
        const grado   = filtroGrado.value;
        const seccion = filtroSeccion.value;

        const params = new URLSearchParams();
        if (grado)   params.append("grado", grado);
        if (seccion) params.append("seccion", seccion);

        fetch(`/api/estudiantes/?${params}`)
            .then(r => r.json())
            .then(data => {
                selectorEstudiante.innerHTML =
                    '<option value="">-- Selecciona un estudiante --</option>';

                if (data.length === 0) {
                    selectorEstudiante.innerHTML +=
                        '<option disabled>No hay estudiantes con esos filtros</option>';
                    return;
                }

                data.forEach(e => {
                    const opt = document.createElement("option");
                    opt.value = e.id;
                    opt.textContent = `${e.nombre} (${e.grado}${e.seccion})`;
                    selectorEstudiante.appendChild(opt);
                });
            });
    }

    filtroGrado.addEventListener("change", cargarEstudiantes);
    filtroSeccion.addEventListener("change", cargarEstudiantes);
});