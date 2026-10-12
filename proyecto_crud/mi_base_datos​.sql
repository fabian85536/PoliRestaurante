CREATE DATABASE IF NOT EXISTS restaurante;
USE restaurante;

CREATE TABLE Mesero (
    id_mesero INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(255),
    usuario VARCHAR(255),
    contrasena VARCHAR(255),
    PRIMARY KEY (id_mesero)
) ENGINE=InnoDB;
CREATE TABLE usuarios (
    id INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    PRIMARY KEY (id)
) ENGINE=InnoDB;

CREATE TABLE PersonalCocina (
    id_cocina INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(255),
    usuario VARCHAR(255),
    contrasena VARCHAR(255),
    PRIMARY KEY (id_cocina)
) ENGINE=InnoDB;


CREATE TABLE Administrador (
    id_administrador INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(255),
    usuario VARCHAR(255),
    contrasena VARCHAR(255),
    PRIMARY KEY (id_administrador)
) ENGINE=InnoDB;


CREATE TABLE Mesa (
    id_mesa INT NOT NULL AUTO_INCREMENT,
    numero INT,
    estado VARCHAR(255),
    id_administrador INT,
    PRIMARY KEY (id_mesa),
    CONSTRAINT fk_mesa_administrador
        FOREIGN KEY (id_administrador)
        REFERENCES Administrador(id_administrador)
) ENGINE=InnoDB;


CREATE TABLE Categoria (
    id_categoria INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(255),
    id_administrador INT,
    PRIMARY KEY (id_categoria),
    CONSTRAINT fk_categoria_administrador
        FOREIGN KEY (id_administrador)
        REFERENCES Administrador(id_administrador)
) ENGINE=InnoDB;


CREATE TABLE Producto (
    id_producto INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(255),
    descripcion VARCHAR(255),
    precio INT,
    id_categoria INT,
    id_administrador INT,
    disponibilidad VARCHAR(255),
    PRIMARY KEY (id_producto),
    CONSTRAINT fk_producto_categoria
        FOREIGN KEY (id_categoria)
        REFERENCES Categoria(id_categoria),
    CONSTRAINT fk_producto_administrador
        FOREIGN KEY (id_administrador)
        REFERENCES Administrador(id_administrador)
) ENGINE=InnoDB;


CREATE TABLE Pedido (
    id_pedido INT NOT NULL AUTO_INCREMENT,
    id_mesero INT,
    id_cocina INT,
    id_administrador INT,
    id_mesa INT NULL,
    tipo_pedido VARCHAR(255),
    nombre_cliente VARCHAR(255),
    estado VARCHAR(255),
    total INT,
    metodo_pago VARCHAR(255),
    fecha_creacion VARCHAR(255),
    fecha_cierre VARCHAR(255),
    PRIMARY KEY (id_pedido),
    CONSTRAINT fk_pedido_mesero
        FOREIGN KEY (id_mesero)
        REFERENCES Mesero(id_mesero),
    CONSTRAINT fk_pedido_cocina
        FOREIGN KEY (id_cocina)
        REFERENCES PersonalCocina(id_cocina),
    CONSTRAINT fk_pedido_administrador
        FOREIGN KEY (id_administrador)
        REFERENCES Administrador(id_administrador),
    CONSTRAINT fk_pedido_mesa
        FOREIGN KEY (id_mesa)
        REFERENCES Mesa(id_mesa)
) ENGINE=InnoDB;


CREATE TABLE Domicilio (
    id_domicilio INT NOT NULL AUTO_INCREMENT,
    id_pedido INT UNIQUE,
    direccion VARCHAR(255),
    telefono VARCHAR(255),
    costo_envio INT,
    PRIMARY KEY (id_domicilio),
    CONSTRAINT fk_domicilio_pedido
        FOREIGN KEY (id_pedido)
        REFERENCES Pedido(id_pedido)
) ENGINE=InnoDB;


CREATE TABLE DetallePedido (
    id_detalle INT NOT NULL AUTO_INCREMENT,
    id_pedido INT,
    id_producto INT,
    cantidad INT,
    precio_unitario INT,
    notas VARCHAR(255),
    PRIMARY KEY (id_detalle),
    CONSTRAINT fk_detalle_pedido
        FOREIGN KEY (id_pedido)
        REFERENCES Pedido(id_pedido),
    CONSTRAINT fk_detalle_producto
        FOREIGN KEY (id_producto)
        REFERENCES Producto(id_producto)
) ENGINE=InnoDB;

SHOW TABLES;


SELECT * FROM Mesero;
SELECT * FROM PersonalCocina;
SELECT * FROM Administrador;
SELECT * FROM Mesa;
SELECT * FROM Categoria;
SELECT * FROM Producto;
SELECT * FROM Pedido;
SELECT * FROM Domicilio;
SELECT * FROM DetallePedido;
SELECT * FROM Usuarios;

    def crear_producto(self, nombre, descripcion, precio, categoria,
                       disponible=True):
        nombre = nombre.strip()
        categoria = categoria.strip()
        precio = float(precio)

        if not nombre:
            raise ValueError("El nombre es obligatorio")
        if not categoria:
            raise ValueError("La categoría es obligatoria")
        if precio <= 0:
            raise ValueError("El precio debe ser mayor que cero")

        conn = self._obtener_conexion()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO productos
                    (nombre, descripcion, precio, categoria, disponible)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (nombre, descripcion, precio, categoria, disponible),
                )
                producto_id = cursor.lastrowid
            conn.commit()
            logging.info("Producto creado: %s", nombre)
            return producto_id
        except Exception:
            conn.rollback()
            logging.exception("Error al crear producto")
            raise

    def obtener_productos(self):
        conn = self._obtener_conexion()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, nombre, descripcion, precio, categoria, disponible
                FROM productos
                ORDER BY id
                """
            )
            columnas = (
                "id", "nombre", "descripcion",
                "precio", "categoria", "disponible"
            )
            return [
                dict(zip(columnas, fila))
                for fila in cursor.fetchall()
            ]

    def obtener_producto(self, producto_id):
        conn = self._obtener_conexion()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, nombre, descripcion, precio, categoria, disponible
                FROM productos
                WHERE id = %s
                """,
                (producto_id,),
            )
            fila = cursor.fetchone()

        if fila is None:
            return None

        columnas = (
            "id", "nombre", "descripcion",
            "precio", "categoria", "disponible"
        )
        return dict(zip(columnas, fila))

    def actualizar_producto(self, producto_id, nombre, descripcion,
                            precio, categoria, disponible=True):
        nombre = nombre.strip()
        categoria = categoria.strip()
        precio = float(precio)

        if not nombre or not categoria:
            raise ValueError("El nombre y la categoría son obligatorios")
        if precio <= 0:
            raise ValueError("El precio debe ser mayor que cero")

        conn = self._obtener_conexion()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE productos
                    SET nombre = %s, descripcion = %s, precio = %s,
                        categoria = %s, disponible = %s
                    WHERE id = %s
                    """,
                    (
                        nombre, descripcion, precio,
                        categoria, disponible, producto_id
                    ),
                )
                actualizado = cursor.rowcount > 0
            conn.commit()
            return actualizado
        except Exception:
            conn.rollback()
            logging.exception("Error al actualizar producto")
            raise

    def eliminar_producto(self, producto_id):
        conn = self._obtener_conexion()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM productos WHERE id = %s",
                    (producto_id,),
                )
                eliminado = cursor.rowcount > 0
            conn.commit()
            return eliminado
        except Exception:
            conn.rollback()
            logging.exception("Error al eliminar producto")
            raise
