import {
  ADMINISTRADOR_SELECCIONADO_KEY,
  API_URL,
  RECURSOS,
} from "./config.js";

const recursoSelect = document.querySelector("#recurso");
const administradorPredeterminado = document.querySelector(
  "#administrador-predeterminado",
);
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
let administradores = [];
let administradoresCargados = false;
let registroEditado = null;
let temporizadorMensaje;
let cargandoRegistros = false;

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

function actualizarOpcionesAdministradores() {
  const valorAnterior = administradorPredeterminado.value;
  const opciones = [crearOpcion("", "Sin asignar")];
  for (const administrador of administradores) {
    const nombre = [administrador.nombre, administrador.usuario]
      .filter(Boolean)
      .join(" · ");
    opciones.push(
      crearOpcion(
        String(administrador.id_administrador),
        `${nombre} (#${administrador.id_administrador})`,
      ),
    );
  }
  administradorPredeterminado.replaceChildren(...opciones);

  const idGuardado = localStorage.getItem(ADMINISTRADOR_SELECCIONADO_KEY) ?? "";
  const existeGuardado = administradores.some(
    (administrador) => String(administrador.id_administrador) === idGuardado,
  );
  const siguienteValor = existeGuardado
    ? idGuardado
    : administradores.some(
          (administrador) =>
            String(administrador.id_administrador) === valorAnterior,
        )
      ? valorAnterior
      : "";
  administradorPredeterminado.value = siguienteValor;
  if (siguienteValor) {
    localStorage.setItem(ADMINISTRADOR_SELECCIONADO_KEY, siguienteValor);
  } else {
    localStorage.removeItem(ADMINISTRADOR_SELECCIONADO_KEY);
  }
}

function crearOpcion(valor, texto) {
  const opcion = document.createElement("option");
  opcion.value = valor;
  opcion.textContent = texto;
  return opcion;
}

async function cargarAdministradores() {
  try {
    administradores = await peticion("/api/administradores");
    administradoresCargados = true;
    actualizarOpcionesAdministradores();
  } catch (error) {
    administradoresCargados = false;
    mostrarMensaje(
      `No se pudieron cargar los administradores: ${error.message}`,
      "danger",
    );
    throw error;
  }
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
      (campo.name.startsWith("id_") && !campo.relation) ||
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
    } else if (campo.relation) {
      const etiqueta = document.createElement("label");
      etiqueta.className = "form-label";
      etiqueta.htmlFor = id;
      etiqueta.textContent = campo.label;
      const select = document.createElement("select");
      select.className = "form-select";
      select.id = id;
      select.name = campo.name;
      const relacionVacia = crearOpcion("", "Sin asignar");
      select.append(relacionVacia);
      for (const administrador of administradores) {
        const nombre = [administrador.nombre, administrador.usuario]
          .filter(Boolean)
          .join(" · ");
        select.append(
          crearOpcion(
            String(administrador[campo.relation.valueField]),
            `${nombre} (#${administrador[campo.relation.valueField]})`,
          ),
        );
      }
      const valorActual = registro?.[campo.name];
      if (
        valorActual != null &&
        !administradores.some(
          (administrador) =>
            String(administrador[campo.relation.valueField]) ===
            String(valorActual),
        )
      ) {
        select.append(
          crearOpcion(
            String(valorActual),
            `Administrador #${valorActual} (no disponible)`,
          ),
        );
      }
      select.value = edicion
        ? valorActual == null
          ? ""
          : String(valorActual)
        : administradorPredeterminado.value;
      columna.append(etiqueta, select);
      camposFormulario.append(columna);
      continue;
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

async function cargarRegistros({ silencioso = false } = {}) {
  if (cargandoRegistros) {
    return;
  }
  cargandoRegistros = true;
  const recurso = recursoSelect.value;
  if (!silencioso) {
    mostrarCargando();
  }
  try {
    const nuevosRegistros = await peticion(`/api/${recurso}`);
    if (recursoSelect.value !== recurso) {
      return;
    }
    registros = nuevosRegistros;
    mostrarRegistros();
  } catch (error) {
    if (recursoSelect.value !== recurso) {
      return;
    }
    if (!silencioso) {
      registros = [];
      mostrarRegistros();
    }
    mostrarMensaje(error.message, "danger");
  } finally {
    cargandoRegistros = false;
    if (recursoSelect.value !== recurso) {
      cargarRegistros();
    }
  }
}

function leerFormulario() {
  const payload = {};
  const recurso = recursoActual();
  for (const campo of recurso.fields) {
    if (
      (campo.name.startsWith("id_") && !campo.relation) ||
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
    if (campo.relation && !valor) {
      payload[campo.name] = null;
      continue;
    }
    if (!valor && (registroEditado || !campo.required)) {
      continue;
    }
    payload[campo.name] =
      campo.type === "number" || campo.relation ? Number(valor) : valor;
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
    if (recursoSelect.value === "administradores") {
      await cargarAdministradores();
      if (!registroEditado) {
        dibujarFormulario();
      }
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

administradorPredeterminado.addEventListener("change", () => {
  const seleccionado = administradorPredeterminado.value;
  if (seleccionado) {
    localStorage.setItem(ADMINISTRADOR_SELECCIONADO_KEY, seleccionado);
  } else {
    localStorage.removeItem(ADMINISTRADOR_SELECCIONADO_KEY);
  }
  if (!registroEditado) {
    dibujarFormulario();
  }
});

recursoSelect.addEventListener("change", () => {
  seccionCrearPedido.classList.toggle("d-none", recursoSelect.value !== "pedidos");
  cancelarEdicion();
  cargarRegistros();
});
botonRecargar.addEventListener("click", cargarRegistros);
window.addEventListener("focus", cargarRegistros);
window.setInterval(() => {
  if (
    document.visibilityState === "visible" &&
    recursoSelect.value === "usuarios" &&
    !registroEditado
  ) {
    cargarRegistros({ silencioso: true });
  }
}, 5000);
botonCancelar.addEventListener("click", cancelarEdicion);

formulario.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const recurso = recursoActual();
  if (
    !administradoresCargados &&
    recurso.fields.some((campo) => campo.relation?.resource === "administradores")
  ) {
    mostrarMensaje(
      "No se pudo cargar la lista de administradores. Recarga antes de guardar.",
      "danger",
    );
    return;
  }
  if (
    formulario.querySelector(
      "select[data-relacion-pendiente], select[data-relacion-error]",
    )
  ) {
    mostrarMensaje(
      "Espera a que se cargue la lista de administradores antes de guardar.",
      "warning",
    );
    return;
  }
  const recursoNombre = recursoSelect.value;
  const payload = leerFormulario();
  const id = registroEditado?.[recursoActual().id];
  const ruta =
    id === undefined
      ? `/api/${recursoNombre}`
      : `/api/${recursoNombre}/${id}`;
  const metodo = id === undefined ? "POST" : "PATCH";

  botonGuardar.disabled = true;
  try {
    await peticion(ruta, {
      method: metodo,
      body: JSON.stringify(payload),
    });
    mostrarMensaje(id === undefined ? "Registro creado." : "Cambios guardados.");
    cancelarEdicion();
    if (recursoNombre === "administradores") {
      await cargarAdministradores();
    }
    await cargarRegistros();
  } catch (error) {
    mostrarMensaje(error.message, "danger");
  } finally {
    botonGuardar.disabled = false;
  }
});
async function inicializar() {
  try {
    await cargarAdministradores();
  } catch {
    administradores = [];
  }
  dibujarFormulario();
  seccionCrearPedido.classList.toggle("d-none", recursoSelect.value !== "pedidos");
  await cargarRegistros();
}

inicializar();
