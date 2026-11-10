import { API_URL, RECURSOS } from "./config.js";

const recursoSelect = document.querySelector("#recurso");
const seccionCrearPedido = document.querySelector("#seccion-crear-pedido");
const encabezadoTabla = document.querySelector("#encabezado-tabla");
const tablaRegistros = document.querySelector("#tabla-registros");
const formulario = document.querySelector("#formulario");
const camposFormulario = document.querySelector("#campos-formulario");
const tituloFormulario = document.querySelector("#titulo-formulario");
const mensaje = document.querySelector("#mensaje");
const botonGuardar = document.querySelector("#btn-guardar");
const botonCancelar = document.querySelector("#btn-cancelar");
const botonRecargar = document.querySelector("#btn-recargar");

let registros = [];
let registroEditado = null;
let temporizadorMensaje;

function recursoActual() {
  return RECURSOS[recursoSelect.value];
}

function mostrarMensaje(texto, tipo = "success") {
  clearTimeout(temporizadorMensaje);
  mensaje.textContent = texto;
  mensaje.className = `alert alert-${tipo}`;
  temporizadorMensaje = setTimeout(() => mensaje.classList.add("d-none"), 5000);
}

async function peticion(ruta, opciones = {}) {
  let respuesta;
  try {
    respuesta = await fetch(`${API_URL}${ruta}`, {
      ...opciones,
      headers: {
        ...(opciones.body ? { "Content-Type": "application/json" } : {}),
        ...opciones.headers,
      },
    });
  } catch {
    throw new Error(
      `No se pudo conectar con ${API_URL}. Comprueba que Flask esté activo y que el cliente se haya abierto con Live Server.`,
    );
  }

  if (respuesta.status === 204) {
    return null;
  }

  const datos = await respuesta.json().catch(() => null);
  if (!respuesta.ok) {
    throw new Error(datos?.error ?? `Error HTTP ${respuesta.status}`);
  }
  return datos;
}

function mostrarCargando() {
  encabezadoTabla.replaceChildren();
  tablaRegistros.replaceChildren();
  const fila = document.createElement("tr");
  const celda = document.createElement("td");
  celda.colSpan = 2;
  celda.className = "text-center text-secondary py-4";
  celda.textContent = "Cargando registros…";
  fila.append(celda);
  tablaRegistros.append(fila);
}

function mostrarRegistros() {
  const recurso = recursoActual();
  const campos = recurso.fields.filter((campo) => !campo.secret);
  const encabezado = document.createElement("tr");
  for (const etiqueta of ["ID", ...campos.map((campo) => campo.label), "Acciones"]) {
    const celda = document.createElement("th");
    celda.scope = "col";
    celda.textContent = etiqueta;
    encabezado.append(celda);
  }
  encabezadoTabla.replaceChildren(encabezado);

  if (registros.length === 0) {
    const fila = document.createElement("tr");
    const celda = document.createElement("td");
    celda.colSpan = campos.length + 2;
    celda.className = "text-center text-secondary py-4";
    celda.textContent = "No hay registros para mostrar.";
    fila.append(celda);
    tablaRegistros.replaceChildren(fila);
    return;
  }

  const filas = registros.map((registro) => {
    const fila = document.createElement("tr");
    const id = registro[recurso.id];
    agregarCelda(fila, id);
    for (const campo of campos) {
      const valor = registro[campo.name];
      agregarCelda(
        fila,
        campo.type === "checkbox"
          ? valor
            ? "Sí"
            : "No"
          : valor ?? "—",
      );
    }

    const acciones = document.createElement("td");
    acciones.className = "text-nowrap";
    acciones.append(
      crearBoton("Editar", "btn btn-sm btn-outline-primary me-2", () =>
        editarRegistro(id),
      ),
      crearBoton("Eliminar", "btn btn-sm btn-outline-danger", () =>
        eliminarRegistro(id),
      ),
    );
    fila.append(acciones);
    return fila;
  });
  tablaRegistros.replaceChildren(...filas);
}

function agregarCelda(fila, valor) {
  const celda = document.createElement("td");
  celda.textContent = String(valor);
  fila.append(celda);
}

function crearBoton(texto, clases, accion) {
  const boton = document.createElement("button");
  boton.type = "button";
  boton.className = clases;
  boton.textContent = texto;
  boton.addEventListener("click", accion);
  return boton;
}

function dibujarFormulario(registro = null) {
  const recurso = recursoActual();
  const edicion = registro !== null;
  camposFormulario.replaceChildren();
  tituloFormulario.textContent = edicion
    ? `Editar ${recurso.label.toLowerCase()} #${registro[recurso.id]}`
    : `Nuevo registro: ${recurso.label.toLowerCase()}`;
  botonGuardar.textContent = edicion ? "Guardar cambios" : "Guardar registro";
  botonCancelar.classList.toggle("d-none", !edicion);

  for (const campo of recurso.fields) {
    if (
      campo.name.startsWith("id_") ||
      campo.computed ||
      (edicion && campo.createOnly)
    ) {
      continue;
    }

    const columna = document.createElement("div");
    columna.className =
      campo.type === "checkbox" ? "col-12" : "col-12 col-md-6 col-xl-4";
    const id = `campo-${campo.name}`;

    if (campo.type === "checkbox") {
      const contenedor = document.createElement("div");
      contenedor.className = "form-check";
      const input = document.createElement("input");
      input.type = "checkbox";
      input.className = "form-check-input";
      input.id = id;
      input.name = campo.name;
      input.checked = registro
        ? Boolean(registro[campo.name])
        : Boolean(campo.defaultValue);
      const etiqueta = document.createElement("label");
      etiqueta.className = "form-check-label";
      etiqueta.htmlFor = id;
      etiqueta.textContent = campo.label;
      contenedor.append(input, etiqueta);
      columna.append(contenedor);
    } else {
      const etiqueta = document.createElement("label");
      etiqueta.className = "form-label";
      etiqueta.htmlFor = id;
      etiqueta.textContent = campo.label;
      const input = document.createElement("input");
      input.type = campo.type ?? "text";
      input.className = "form-control";
      input.id = id;
      input.name = campo.name;
      input.autocomplete = campo.type === "password" ? "new-password" : "off";
      input.required = Boolean(campo.required && !edicion);
      if (campo.type === "number") {
        input.step = "1";
      }
      if (registro && !campo.secret) {
        input.value = registro[campo.name] ?? "";
      }
      if (campo.secret && edicion) {
        input.placeholder = "Dejar vacío para conservar la contraseña";
      }
      columna.append(etiqueta, input);
    }
    camposFormulario.append(columna);
  }
}

async function cargarRegistros() {
  mostrarCargando();
  try {
    registros = await peticion(`/api/${recursoSelect.value}`);
    mostrarRegistros();
  } catch (error) {
    registros = [];
    mostrarRegistros();
    mostrarMensaje(error.message, "danger");
  }
}

function leerFormulario() {
  const payload = {};
  const recurso = recursoActual();
  for (const campo of recurso.fields) {
    if (
      campo.name.startsWith("id_") ||
      campo.computed ||
      (registroEditado && campo.createOnly)
    ) {
      continue;
    }
    const control = formulario.elements.namedItem(campo.name);
    if (campo.type === "checkbox") {
      payload[campo.name] = control.checked;
      continue;
    }
    const valor = control.value.trim();
    if (!valor && (registroEditado || !campo.required)) {
      continue;
    }
    payload[campo.name] = campo.type === "number" ? Number(valor) : valor;
  }
  return payload;
}

function editarRegistro(id) {
  const recurso = recursoActual();
  registroEditado = registros.find((registro) => registro[recurso.id] === id);
  if (!registroEditado) {
    mostrarMensaje("No se encontró el registro seleccionado.", "warning");
    return;
  }
  dibujarFormulario(registroEditado);
  formulario.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function eliminarRegistro(id) {
  const recurso = recursoActual();
  if (!window.confirm(`¿Eliminar el registro #${id} de ${recurso.label}?`)) {
    return;
  }
  try {
    await peticion(`/api/${recursoSelect.value}/${id}`, { method: "DELETE" });
    mostrarMensaje("Registro eliminado.");
    if (registroEditado?.[recurso.id] === id) {
      cancelarEdicion();
    }
    await cargarRegistros();
  } catch (error) {
    mostrarMensaje(error.message, "danger");
  }
}

function cancelarEdicion() {
  registroEditado = null;
  formulario.reset();
  dibujarFormulario();
}

recursoSelect.replaceChildren(
  ...Object.entries(RECURSOS).map(([valor, recurso]) => {
    const opcion = document.createElement("option");
    opcion.value = valor;
    opcion.textContent = recurso.label;
    return opcion;
  }),
);

recursoSelect.addEventListener("change", () => {
  seccionCrearPedido.classList.toggle("d-none", recursoSelect.value !== "pedidos");
  cancelarEdicion();
  cargarRegistros();
});
botonRecargar.addEventListener("click", cargarRegistros);
window.addEventListener("focus", cargarRegistros);
botonCancelar.addEventListener("click", cancelarEdicion);

formulario.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const recurso = recursoSelect.value;
  const payload = leerFormulario();
  const id = registroEditado?.[recursoActual().id];
  const ruta = id === undefined ? `/api/${recurso}` : `/api/${recurso}/${id}`;
  const metodo = id === undefined ? "POST" : "PATCH";

  botonGuardar.disabled = true;
  try {
    await peticion(ruta, {
      method: metodo,
      body: JSON.stringify(payload),
    });
    mostrarMensaje(id === undefined ? "Registro creado." : "Cambios guardados.");
    cancelarEdicion();
    await cargarRegistros();
  } catch (error) {
    mostrarMensaje(error.message, "danger");
  } finally {
    botonGuardar.disabled = false;
  }
});
dibujarFormulario();
dibujarFormulario();
seccionCrearPedido.classList.toggle("d-none", recursoSelect.value !== "pedidos");
cargarRegistros();
