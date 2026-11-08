import { API_URL } from "./config.js";

const formulario = document.querySelector("#formulario-pedido");
const filasProductos = document.querySelector("#filas-productos");
const mensaje = document.querySelector("#mensaje");
const mensajeProductos = document.querySelector("#mensaje-productos");
const botonAgregarProducto = document.querySelector("#btn-agregar-producto");
const botonCrearPedido = document.querySelector("#btn-crear-pedido");

let productosDisponibles = [];
let secuenciaFila = 0;

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

  const datos = await respuesta.json().catch(() => null);
  if (!respuesta.ok) {
    throw new Error(datos?.error ?? `Error HTTP ${respuesta.status}`);
  }
  return datos;
}

function mostrarMensaje(texto, tipo = "success") {
  mensaje.textContent = texto;
  mensaje.className = `alert alert-${tipo}`;
}

function actualizarTotal() {
  const total = [...filasProductos.children].reduce((suma, fila) => {
    const cantidad = Number(fila.querySelector('[name="cantidad"]').value);
    const precio = Number(fila.querySelector('[name="precio_unitario"]').value);
    if (!Number.isSafeInteger(cantidad) || !Number.isSafeInteger(precio)) {
      return suma;
    }
    return suma + cantidad * precio;
  }, 0);
  formulario.elements.namedItem("total").value = String(total);
}

function actualizarBotonesEliminar() {
  const botones = filasProductos.querySelectorAll("[data-eliminar-producto]");
  for (const boton of botones) {
    boton.disabled = botones.length === 1;
  }
}

function agregarFilaProducto() {
  const fila = document.createElement("div");
  fila.className = "row g-3 align-items-end border rounded p-3 mx-0";
  const numeroFila = secuenciaFila;
  secuenciaFila += 1;

  const selector = document.createElement("select");
  selector.className = "form-select";
  selector.name = "id_producto";
  selector.required = true;
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "Selecciona un producto";
  selector.append(placeholder);
  for (const producto of productosDisponibles) {
    const opcion = document.createElement("option");
    opcion.value = String(producto.id);
    opcion.textContent = `${producto.nombre} — $${producto.precio}`;
    opcion.dataset.precio = String(producto.precio);
    selector.append(opcion);
  }
  selector.id = `producto-${numeroFila}`;

  const cantidad = document.createElement("input");
  cantidad.className = "form-control";
  cantidad.type = "number";
  cantidad.name = "cantidad";
  cantidad.min = "1";
  cantidad.step = "1";
  cantidad.required = true;
  cantidad.id = `cantidad-${numeroFila}`;

  const precio = document.createElement("input");
  precio.className = "form-control";
  precio.type = "number";
  precio.name = "precio_unitario";
  precio.readOnly = true;
  precio.placeholder = "Lo determina el producto";
  precio.id = `precio-${numeroFila}`;

  const notas = document.createElement("input");
  notas.className = "form-control";
  notas.type = "text";
  notas.name = "notas";
  notas.id = `notas-${numeroFila}`;

  for (const [nombre, control, clase] of [
    ["Producto", selector, "col-12 col-lg-3"],
    ["Cantidad", cantidad, "col-6 col-lg-2"],
    ["Precio unitario", precio, "col-6 col-lg-2"],
    ["Notas", notas, "col-12 col-lg-3"],
  ]) {
    const columna = document.createElement("div");
    columna.className = clase;
    const etiqueta = document.createElement("label");
    etiqueta.className = "form-label";
    etiqueta.htmlFor = control.id;
    etiqueta.textContent = nombre;
    columna.append(etiqueta, control);
    fila.append(columna);
  }

  const columnaAccion = document.createElement("div");
  columnaAccion.className = "col-12 col-lg-2";
  const botonEliminar = document.createElement("button");
  botonEliminar.type = "button";
  botonEliminar.className = "btn btn-outline-danger w-100";
  botonEliminar.textContent = "Quitar";
  botonEliminar.dataset.eliminarProducto = "";
  botonEliminar.addEventListener("click", () => {
    fila.remove();
    actualizarBotonesEliminar();
    actualizarTotal();
  });
  columnaAccion.append(botonEliminar);
  fila.append(columnaAccion);
  filasProductos.append(fila);
  actualizarBotonesEliminar();
  actualizarTotal();
}

async function cargarProductos() {
  try {
    productosDisponibles = await peticion("/api/productos");
    if (productosDisponibles.length === 0) {
      mensajeProductos.textContent =
        "No hay productos registrados. Créelos primero en Administración.";
      botonCrearPedido.disabled = true;
      botonAgregarProducto.disabled = true;
      return;
    }
    mensajeProductos.textContent =
      "El precio unitario se obtiene del producto y el total se calcula automáticamente.";
    agregarFilaProducto();
  } catch (error) {
    mensajeProductos.textContent = `No se pudo cargar el catálogo: ${error.message}`;
    botonCrearPedido.disabled = true;
    botonAgregarProducto.disabled = true;
  }
}

filasProductos.addEventListener("change", (evento) => {
  if (evento.target.name !== "id_producto") {
    return;
  }
  const fila = evento.target.closest(".row");
  fila.querySelector('[name="precio_unitario"]').value =
    evento.target.selectedOptions[0]?.dataset.precio ?? "";
  actualizarTotal();
});

filasProductos.addEventListener("input", (evento) => {
  if (evento.target.name === "cantidad") {
    actualizarTotal();
  }
});

botonAgregarProducto.addEventListener("click", agregarFilaProducto);

formulario.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const datos = new FormData(formulario);
  const pedido = {};
  for (const campo of ["tipo_pedido", "nombre_cliente", "estado"]) {
    const valor = String(datos.get(campo) ?? "").trim();
    if (valor) {
      pedido[campo] = valor;
    }
  }
  pedido.total = Number(datos.get("total"));

  const detalles = [...filasProductos.children].map((fila) => {
    const cantidad = Number(fila.querySelector('[name="cantidad"]').value);
    const precio = Number(fila.querySelector('[name="precio_unitario"]').value);
    const detalle = {
      id_producto: Number(fila.querySelector('[name="id_producto"]').value),
      cantidad,
      precio_unitario: precio,
    };
    const notas = fila.querySelector('[name="notas"]').value.trim();
    if (notas) {
      detalle.notas = notas;
    }
    return detalle;
  });

  botonCrearPedido.disabled = true;
  try {
    const creado = await peticion("/api/pedidos/con-detalles", {
      method: "POST",
      body: JSON.stringify({ pedido, detalles }),
    });
    mostrarMensaje(
      `Pedido #${creado.pedido.id_pedido} creado con ${creado.detalles.length} producto(s).`,
    );
    formulario.reset();
    filasProductos.replaceChildren();
    agregarFilaProducto();
  } catch (error) {
    mostrarMensaje(error.message, "danger");
  } finally {
    botonCrearPedido.disabled = false;
  }
});

cargarProductos();
