export const API_URL = "http://127.0.0.1:5000";

export const RECURSOS = {
  usuarios: {
    label: "Usuarios",
    id: "id",
    fields: [
      { name: "nombre", label: "Nombre", required: true },
      { name: "email", label: "Correo electrónico", type: "email", required: true, createOnly: true },
    ],
  },
  productos: {
    label: "Productos",
    id: "id",
    fields: [
      { name: "nombre", label: "Nombre", required: true },
      { name: "descripcion", label: "Descripción" },
      { name: "precio", label: "Precio", type: "number", required: true },
      { name: "id_categoria", label: "ID de categoría", type: "number" },
      { name: "id_administrador", label: "ID de administrador", type: "number" },
      { name: "disponible", label: "Disponible", type: "checkbox", defaultValue: true },
    ],
  },
  meseros: {
    label: "Meseros",
    id: "id_mesero",
    fields: [
      { name: "nombre", label: "Nombre", required: true },
      { name: "usuario", label: "Usuario", required: true },
      { name: "contrasena", label: "Contraseña", type: "password", required: true, secret: true },
    ],
  },
  administradores: {
    label: "Administradores",
    id: "id_administrador",
    fields: [
      { name: "nombre", label: "Nombre", required: true },
      { name: "usuario", label: "Usuario", required: true },
      { name: "contrasena", label: "Contraseña", type: "password", required: true, secret: true },
    ],
  },
  personal_cocina: {
    label: "Personal de cocina",
    id: "id_cocina",
    fields: [
      { name: "nombre", label: "Nombre", required: true },
      { name: "usuario", label: "Usuario", required: true },
      { name: "contrasena", label: "Contraseña", type: "password", required: true, secret: true },
    ],
  },
  mesas: {
    label: "Mesas",
    id: "id_mesa",
    fields: [
      { name: "numero", label: "Número de mesa", type: "number", required: true },
      { name: "estado", label: "Estado", required: true },
      { name: "id_administrador", label: "ID de administrador", type: "number" },
    ],
  },
  pedidos: {
    label: "Pedidos",
    id: "id_pedido",
    fields: [
      { name: "id_mesero", label: "ID de mesero", type: "number" },
      { name: "id_cocina", label: "ID de personal de cocina", type: "number" },
      { name: "id_administrador", label: "ID de administrador", type: "number" },
      { name: "id_mesa", label: "ID de mesa", type: "number" },
      { name: "tipo_pedido", label: "Tipo de pedido" },
      { name: "nombre_cliente", label: "Nombre del cliente" },
      { name: "estado", label: "Estado" },
      { name: "total", label: "Total", type: "number" },
      { name: "metodo_pago", label: "Método de pago" },
      { name: "fecha_creacion", label: "Fecha de creación" },
      { name: "fecha_cierre", label: "Fecha de cierre" },
    ],
  },
  domicilios: {
    label: "Domicilios",
    id: "id_domicilio",
    fields: [
      { name: "id_pedido", label: "ID de pedido", type: "number" },
      { name: "direccion", label: "Dirección" },
      { name: "telefono", label: "Teléfono" },
      { name: "costo_envio", label: "Costo de envío", type: "number" },
    ],
  },
  detalles_pedido: {
    label: "Detalles de pedido",
    id: "id_detalle",
    fields: [
      { name: "id_pedido", label: "ID de pedido", type: "number" },
      { name: "id_producto", label: "ID de producto", type: "number" },
      { name: "cantidad", label: "Cantidad", type: "number" },
      { name: "precio_unitario", label: "Precio unitario", type: "number" },
      { name: "notas", label: "Notas" },
    ],
  },
};
