import logging

import mysql.connector
from config import obtener_configuracion_bd
from validation import validar_email

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class Database:
    def __init__(self):
        self.conn = None

    def conectar(self):
        try:
            self.conn = mysql.connector.connect(**obtener_configuracion_bd())
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            print("Conectado a BD")
        except Exception:
            if self.conn is not None and self.conn.is_connected():
                self.conn.close()
                self.conn = None
            logging.exception("No se pudo conectar a MySQL")
            raise

    def desconectar(self):
        if self.conn is not None and self.conn.is_connected():
            self.conn.close()
            logging.info("Conexión a MySQL cerrada")

    def _obtener_conexion(self):
        if self.conn is None or not self.conn.is_connected():
            raise RuntimeError("Primero debes llamar a conectar()")
        return self.conn

    def crear_usuario(self, nombre, email):
        if not validar_email(email):
            raise ValueError("Email inválido")

        conn = self._obtener_conexion()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO usuarios (nombre, email)
                    VALUES (%s, %s)
                    """,
                    (nombre, email),
                )
                usuario_id = cursor.lastrowid
            conn.commit()
            logging.info("Usuario creado: %s", email)
            return usuario_id
        except Exception:
            conn.rollback()
            logging.exception("Error al crear usuario")
            raise

    def obtener_usuarios(self):
        conn = self._obtener_conexion()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, nombre, email FROM usuarios ORDER BY id")
            return [
                {"id": fila[0], "nombre": fila[1], "email": fila[2]}
                for fila in cursor.fetchall()
            ]

    def obtener_por_email(self, email):
        conn = self._obtener_conexion()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, nombre, email FROM usuarios WHERE email = %s",
                (email,),
            )
            fila = cursor.fetchone()
        if fila is None:
            return None
        return {"id": fila[0], "nombre": fila[1], "email": fila[2]}

    def actualizar(self, email, nuevo_nombre):
        conn = self._obtener_conexion()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE usuarios SET nombre = %s WHERE email = %s",
                    (nuevo_nombre, email),
                )
                actualizado = cursor.rowcount > 0
            conn.commit()
            return actualizado
        except Exception:
            conn.rollback()
            logging.exception("Error al actualizar usuario")
            raise

    def eliminar(self, email):
        conn = self._obtener_conexion()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM usuarios WHERE email = %s", (email,))
                eliminado = cursor.rowcount > 0
            conn.commit()
            return eliminado
        except Exception:
            conn.rollback()
            logging.exception("Error al eliminar usuario")
            raise