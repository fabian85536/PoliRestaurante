import {
  ADMINISTRADOR_SELECCIONADO_KEY,
  API_URL,
} from "./config.js";

const formulario = document.querySelector("#formulario-pedido");
const catalogo = document.querySelector("#catalogo-productos");
const carrito = document.querySelector("#carrito-productos");
const carritoVacio = document.querySelector("#carrito-vacio");
const contadorProductos = document.querySelector("#cantidad-productos");
const totalPedido = document.querySelector("#total-pedido");
const mensaje = document.querySelector("#mensaje");
const mensajeProductos = document.querySelector("#mensaje-productos");
const busqueda = document.querySelector("#buscar-producto");
const botonCrearPedido = document.querySelector("#btn-crear-pedido");
const pedidoExistente = document.querySelector("#pedido-existente");
const tipoPedido = document.querySelector("#pedido-tipo");
const nombreCliente = document.querySelector("#pedido-cliente");

const formatoPrecio = new Intl.NumberFormat("es-CO", {
  style: "currency",
  currency: "COP",
  maximumFractionDigits: 0,
});

let productosDisponibles = [];
let pedidosDisponibles = [];
const productosSeleccionados = new Map();
let enviandoPedido = false;

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

function crearElemento(etiqueta, clase, texto) {
  const elemento = document.createElement(etiqueta);
  if (clase) {
    elemento.className = clase;
  }
  if (texto !== undefined) {
    elemento.textContent = texto;
  }
  return elemento;
}

function dibujarCatalogo(filtro = "") {
  const termino = filtro.trim().toLocaleLowerCase("es");
  const productos = productosDisponibles.filter((producto) =>
    producto.nombre.toLocaleLowerCase("es").includes(termino),
  );
  const tarjetas = productos.map((producto) => {
    const columna = crearElemento("div", "col-12 col-sm-6");
    const tarjeta = crearElemento("article", "card product-card h-100");
    const cuerpo = crearElemento("div", "card-body d-flex flex-column p-4");
    const detalle = crearElemento(
      "p",
      "product-description text-secondary flex-grow-1",
      producto.descripcion || "Preparado al momento con ingredientes frescos.",
    );
    const encabezado = crearElemento(
      "div",
      "d-flex justify-content-between align-items-start gap-2 mb-2",
    );
    encabezado.append(
      crearElemento("h3", "h5 product-name mb-0", producto.nombre),
      crearElemento("span", "product-mark", "PR"),
    );
    cuerpo.append(
      encabezado,
      crearElemento("span", "product-availability mb-3", "Disponible"),
      detalle,
    );

    const pie = crearElemento(
      "div",
      "d-flex justify-content-between align-items-center gap-2 pt-3 border-top",
    );
    pie.append(
      crearElemento(
        "span",
        "product-price",
        formatoPrecio.format(producto.precio),
      ),
    );
    const agregar = crearElemento("button", "btn btn-primary btn-sm", "Agregar");
    agregar.type = "button";
    agregar.dataset.agregarProducto = String(producto.id);
    agregar.setAttribute("aria-label", `Agregar ${producto.nombre} al pedido`);
    pie.append(agregar);
    cuerpo.append(pie);
    tarjeta.append(cuerpo);
    columna.append(tarjeta);
    return columna;
  });
  catalogo.replaceChildren(...tarjetas);

  if (productos.length === 0) {
    mensajeProductos.textContent = termino
      ? "No encontramos productos con ese nombre."
      : "No hay productos disponibles en este momento.";
  } else {
    mensajeProductos.textContent = "";
  }
}

function actualizarResumen() {
  const seleccion = [...productosSeleccionados.values()];
  const cantidadTotal = seleccion.reduce((suma, item) => suma + item.cantidad, 0);
  const total = seleccion.reduce(
    (suma, item) => suma + item.producto.precio * item.cantidad,
    0,
  );

  carritoVacio.classList.toggle("d-none", seleccion.length > 0);
  contadorProductos.textContent = `${cantidadTotal} ${
    cantidadTotal === 1 ? "producto" : "productos"
  }`;
  totalPedido.textContent = formatoPrecio.format(total);
  botonCrearPedido.textContent = pedidoExistente.value
    ? "Agregar productos al pedido"
    : "Confirmar pedido";
  botonCrearPedido.disabled = seleccion.length === 0 || enviandoPedido;
}

function dibujarCarrito() {
  const filas = [...productosSeleccionados.entries()].map(
    ([id, seleccion]) => {
      const fila = crearElemento("div", "cart-item");
      const encabezado = crearElemento(
        "div",
        "d-flex justify-content-between gap-2",
      );
      const nombre = crearElemento(
        "h3",
        "h6 mb-1",
        seleccion.producto.nombre,
      );
      const subtotal = crearElemento(
        "span",
        "small fw-semibold text-nowrap",
        formatoPrecio.format(seleccion.producto.precio * seleccion.cantidad),
      );
      encabezado.append(nombre, subtotal);

      const controles = crearElemento(
        "div",
        "d-flex justify-content-between align-items-center mt-2",
      );
      const cantidad = crearElemento("div", "quantity-control");
      const disminuir = crearElemento("button", "quantity-button", "−");
      disminuir.type = "button";
      disminuir.dataset.cambiarCantidad = id;
      disminuir.dataset.cambio = "-1";
      disminuir.setAttribute("aria-label", `Quitar una unidad de ${seleccion.producto.nombre}`);
      const etiquetaCantidad = crearElemento(
        "span",
        "quantity-value",
        String(seleccion.cantidad),
      );
      const aumentar = crearElemento("button", "quantity-button", "+");
      aumentar.type = "button";
      aumentar.dataset.cambiarCantidad = id;
      aumentar.dataset.cambio = "1";
      aumentar.setAttribute("aria-label", `Agregar una unidad de ${seleccion.producto.nombre}`);
      cantidad.append(disminuir, etiquetaCantidad, aumentar);
      const quitar = crearElemento("button", "btn btn-link btn-sm p-0 text-danger", "Quitar");
      quitar.type = "button";
      quitar.dataset.quitarProducto = id;
      controles.append(cantidad, quitar);

      const etiquetaNotas = crearElemento("label", "form-label small mt-3", "Notas para cocina");
      const notas = crearElemento("input", "form-control form-control-sm");
      notas.type = "text";
      notas.maxLength = 255;
      notas.placeholder = "Opcional";
      notas.value = seleccion.notas;
      notas.dataset.notasProducto = id;
      etiquetaNotas.htmlFor = `notas-producto-${id}`;
      notas.id = etiquetaNotas.htmlFor;
      fila.append(encabezado, controles, etiquetaNotas, notas);
      return fila;
    },
  );
  carrito.replaceChildren(...filas);
  actualizarResumen();
}

async function cargarProductos() {
  try {
    const productos = await peticion("/api/productos");
    productosDisponibles = productos.filter((producto) => producto.disponible);
    if (productosDisponibles.length === 0) {
      catalogo.replaceChildren();
      mensajeProductos.textContent =
        "No hay productos disponibles. Revisa el catálogo desde Administración.";
      return;
    }
    dibujarCatalogo();
  } catch (error) {
    catalogo.replaceChildren();
    mensajeProductos.textContent = `No se pudo cargar el menú: ${error.message}`;
  }
}

async function cargarPedidos() {
  try {
    const seleccionAnterior = pedidoExistente.value;
    pedidosDisponibles = await peticion("/api/pedidos");
    const opciones = [
      crearElemento("option", "", "Crear un pedido nuevo"),
      ...pedidosDisponibles.map((pedido) => {
        const detalles = [
          pedido.tipo_pedido,
          pedido.nombre_cliente,
          pedido.estado,
        ].filter(Boolean);
        const descripcion = detalles.length
          ? detalles.join(" · ")
          : "Sin datos adicionales";
        const opcion = crearElemento(
          "option",
          "",
          `Pedido #${pedido.id_pedido} · ${descripcion}`,
        );
        opcion.value = String(pedido.id_pedido);
        return opcion;
      }),
    ];
    pedidoExistente.replaceChildren(...opciones);
    if (pedidosDisponibles.some(
      (pedido) => String(pedido.id_pedido) === seleccionAnterior,
    )) {
      pedidoExistente.value = seleccionAnterior;
    }
    actualizarResumen();
  } catch (error) {
    mostrarMensaje(
      `No se pudieron cargar los pedidos existentes: ${error.message}`,
      "danger",
    );
  }
}

function actualizarDatosPedidoSeleccionado() {
  const pedido = pedidosDisponibles.find(
    (item) => String(item.id_pedido) === pedidoExistente.value,
  );
  if (!pedido) {
    actualizarResumen();
    return;
  }

  if (
    pedido.tipo_pedido &&
    ![...tipoPedido.options].some(
      (opcion) => opcion.value === pedido.tipo_pedido,
    )
  ) {
    tipoPedido.add(
      crearElemento("option", "", pedido.tipo_pedido),
    );
    tipoPedido.lastElementChild.value = pedido.tipo_pedido;
  }
  tipoPedido.value = pedido.tipo_pedido ?? "";
  nombreCliente.value = pedido.nombre_cliente ?? "";
  actualizarResumen();
}

catalogo.addEventListener("click", (evento) => {
  const boton = evento.target.closest("[data-agregar-producto]");
  if (!boton) {
    return;
  }
  const producto = productosDisponibles.find(
    (item) => String(item.id) === boton.dataset.agregarProducto,
  );
  if (!producto) {
    mostrarMensaje("El producto seleccionado ya no está disponible.", "warning");
    return;
  }

  const seleccionado = productosSeleccionados.get(boton.dataset.agregarProducto);
  productosSeleccionados.set(boton.dataset.agregarProducto, {
    producto,
    cantidad: (seleccionado?.cantidad ?? 0) + 1,
    notas: seleccionado?.notas ?? "",
  });
  dibujarCarrito();
  mostrarMensaje(`${producto.nombre} agregado al pedido.`);
});

carrito.addEventListener("click", (evento) => {
  const botonCantidad = evento.target.closest("[data-cambiar-cantidad]");
  if (botonCantidad) {
    const id = botonCantidad.dataset.cambiarCantidad;
    const seleccionado = productosSeleccionados.get(id);
    const cantidad = seleccionado.cantidad + Number(botonCantidad.dataset.cambio);
    if (cantidad === 0) {
      productosSeleccionados.delete(id);
    } else {
      productosSeleccionados.set(id, { ...seleccionado, cantidad });
    }
    dibujarCarrito();
    return;
  }

  const botonQuitar = evento.target.closest("[data-quitar-producto]");
  if (botonQuitar) {
    productosSeleccionados.delete(botonQuitar.dataset.quitarProducto);
    dibujarCarrito();
  }
});

carrito.addEventListener("input", (evento) => {
  const campoNotas = evento.target.closest("[data-notas-producto]");
  if (!campoNotas) {
    return;
  }
  const seleccionado = productosSeleccionados.get(campoNotas.dataset.notasProducto);
  seleccionado.notas = campoNotas.value;
});

busqueda.addEventListener("input", () => dibujarCatalogo(busqueda.value));
pedidoExistente.addEventListener("change", actualizarDatosPedidoSeleccionado);

formulario.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  if (productosSeleccionados.size === 0 || enviandoPedido) {
    return;
  }

  const datos = new FormData(formulario);
  const seleccion = [...productosSeleccionados.values()];
  const pedido = {
    tipo_pedido: String(datos.get("tipo_pedido") ?? "").trim(),
    estado: "Pendiente",
  };
  const administradorId = localStorage.getItem(
    ADMINISTRADOR_SELECCIONADO_KEY,
  );
  if (administradorId) {
    pedido.id_administrador = Number(administradorId);
  }
  const cliente = String(datos.get("nombre_cliente") ?? "").trim();
  if (cliente) {
    pedido.nombre_cliente = cliente;
  }
  const detalles = seleccion.map(({ producto, cantidad, notas }) => {
    const detalle = {
      id_producto: producto.id,
      cantidad,
      precio_unitario: producto.precio,
    };
    if (notas.trim()) {
      detalle.notas = notas.trim();
    }
    return detalle;
  });

  enviandoPedido = true;
  actualizarResumen();
  try {
    const idPedido = pedidoExistente.value;
    const ruta = idPedido
      ? `/api/pedidos/${idPedido}/con-detalles`
      : "/api/pedidos/con-detalles";
    const datosPedido = idPedido
      ? { tipo_pedido: pedido.tipo_pedido, nombre_cliente: cliente, detalles }
      : { pedido, detalles };
    const creado = await peticion(ruta, {
      method: "POST",
      body: JSON.stringify(datosPedido),
    });
    mostrarMensaje(
      idPedido
        ? `Productos agregados al pedido #${creado.pedido.id_pedido}. Total actualizado: ${formatoPrecio.format(creado.pedido.total)}.`
        : `¡Pedido confirmado! Número #${creado.pedido.id_pedido}. Total: ${formatoPrecio.format(creado.pedido.total)}.`,
    );
    formulario.reset();
    productosSeleccionados.clear();
    dibujarCarrito();
    await cargarPedidos();
    window.scrollTo({ top: 0, behavior: "smooth" });
  } catch (error) {
    mostrarMensaje(error.message, "danger");
  } finally {
    enviandoPedido = false;
    actualizarResumen();
  }
});

actualizarResumen();
cargarProductos();
cargarPedidos();
