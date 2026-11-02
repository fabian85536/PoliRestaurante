import { API_URL, RECURSOS } from "./config.js";

const recursoSelect = document.querySelector("#recurso");
const encabezadoTabla = document.querySelector("#encabezado-tabla");
const tablaRegistros = document.querySelector("#tabla-registros");
const formulario = document.querySelector("#formulario");
const camposFormulario = document.querySelector("#campos-formulario");
const tituloFormulario = document.querySelector("#titulo-formulario");
const mensaje = document.querySelector("#mensaje");
const botonGuardar = document.querySelector("#btn-guardar");
const botonCancelar = document.querySelector("#btn-cancelar");
const botonRecargar = document.querySelector("#btn-recargar");
const formularioPedidoCompleto = document.querySelector(
  "#formulario-pedido-completo",
);
const filasDetalles = document.querySelector("#filas-detalles");
const botonAgregarDetalle = document.querySelector("#btn-agregar-detalle");

let registros = [];
let registroEditado = null;
let temporizadorMensaje;
let secuenciaDetalle = 0;

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

function actualizarBotonesEliminarDetalle() {
  const botones = filasDetalles.querySelectorAll("[data-eliminar-detalle]");
  for (const boton of botones) {
    boton.disabled = botones.length === 1;
  }
}

function agregarFilaDetalle() {
  const numeroFila = secuenciaDetalle;
  secuenciaDetalle += 1;
  const fila = document.createElement("div");
  fila.className = "row g-3 align-items-end border rounded p-3 mx-0";
  const campos = [
    { name: "id_producto", label: "ID del producto", type: "number", min: "1" },
    { name: "cantidad", label: "Cantidad", type: "number", min: "1" },
    {
      name: "precio_unitario",
      label: "Precio unitario",
      type: "number",
      min: "0",
    },
    { name: "notas", label: "Notas", type: "text" },
  ];

  for (const campo of campos) {
    const columna = document.createElement("div");
    columna.className =
      campo.name === "notas" ? "col-12 col-lg-3" : "col-6 col-lg-2";
    const etiqueta = document.createElement("label");
    etiqueta.className = "form-label";
    etiqueta.textContent = campo.label;
    const input = document.createElement("input");
    input.className = "form-control";
    input.name = campo.name;
    input.type = campo.type;
    input.required = campo.type === "number";
    if (campo.min !== undefined) {
      input.min = campo.min;
      input.step = "1";
    }
    etiqueta.htmlFor = `detalle-${campo.name}-${numeroFila}`;
    input.id = etiqueta.htmlFor;
    columna.append(etiqueta, input);
    fila.append(columna);
  }

  const columnaAccion = document.createElement("div");
  columnaAccion.className = "col-12 col-lg-2";
  const eliminar = crearBoton(
    "Quitar",
    "btn btn-outline-danger w-100",
    () => {
      fila.remove();
      actualizarBotonesEliminarDetalle();
    },
  );
  eliminar.dataset.eliminarDetalle = "";
  columnaAccion.append(eliminar);
  fila.append(columnaAccion);
  filasDetalles.append(fila);
  actualizarBotonesEliminarDetalle();
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
    if (edicion && campo.createOnly) {
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
    if (registroEditado && campo.createOnly) {
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
  cancelarEdicion();
  cargarRegistros();
});
botonRecargar.addEventListener("click", cargarRegistros);
botonCancelar.addEventListener("click", cancelarEdicion);
botonAgregarDetalle.addEventListener("click", agregarFilaDetalle);

formularioPedidoCompleto.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const datos = new FormData(formularioPedidoCompleto);
  const pedido = {};
  for (const campo of ["tipo_pedido", "nombre_cliente", "estado"]) {
    const valor = String(datos.get(campo) ?? "").trim();
    if (valor) {
      pedido[campo] = valor;
    }
  }
  const total = String(datos.get("total") ?? "").trim();
  if (total) {
    pedido.total = Number(total);
  }
  const detalles = [...filasDetalles.children].map((fila) => {
    const campos = Object.fromEntries(
      [...fila.querySelectorAll("input")].map((input) => [
        input.name,
        input.value,
      ]),
    );
    const detalle = {
      id_producto: Number(campos.get("id_producto")),
      cantidad: Number(campos.get("cantidad")),
      precio_unitario: Number(campos.get("precio_unitario")),
    };
    const notas = String(campos.get("notas") ?? "").trim();
    if (notas) {
      detalle.notas = notas;
    }
    return detalle;
  });
  const botonGuardarPedido = formularioPedidoCompleto.querySelector(
    'button[type="submit"]',
  );
  botonGuardarPedido.disabled = true;
  try {
    const creado = await peticion("/api/pedidos/con-detalles", {
      method: "POST",
      body: JSON.stringify({ pedido, detalles }),
    });
    mostrarMensaje(
      `Pedido #${creado.pedido.id_pedido} creado con ${creado.detalles.length} detalle(s).`,
    );
    formularioPedidoCompleto.reset();
    filasDetalles.replaceChildren();
    agregarFilaDetalle();
    if (recursoSelect.value === "pedidos") {
      await cargarRegistros();
    }
  } catch (error) {
    mostrarMensaje(error.message, "danger");
  } finally {
    botonGuardarPedido.disabled = false;
  }
});

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
agregarFilaDetalle();
cargarRegistros();
