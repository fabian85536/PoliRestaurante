import logging

from models.usuario import Usuario
from validation import validar_email


class UsuarioDAO:
    def __init__(self, conexion):
        self.conexion = conexion

    def _obtener_conexion(self):
        if self.conexion is None or not self.conexion.is_connected():
            raise RuntimeError("Primero debes llamar a conectar()")
        return self.conexion

    def crear_usuario(self, nombre, email):
        if not validar_email(email):
            raise ValueError("Email inválido")

        conexion = self._obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO usuarios (nombre, email)
                    VALUES (%s, %s)
                    """,
                    (nombre, email),
                )
                usuario_id = cursor.lastrowid
            conexion.commit()
            logging.info("Usuario creado: %s", email)
            return usuario_id
        except Exception:
            conexion.rollback()
            logging.exception("Error al crear usuario")
            raise

    def obtener_usuarios(self):
        conexion = self._obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id, nombre, email FROM usuarios ORDER BY id")
            return [Usuario(*fila) for fila in cursor.fetchall()]

    def obtener_por_email(self, email):
        conexion = self._obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT id, nombre, email FROM usuarios WHERE email = %s",
                (email,),
            )
            fila = cursor.fetchone()
        if fila is None:
            return None
        return Usuario(*fila)

    def actualizar(self, email, nuevo_nombre):
        conexion = self._obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "UPDATE usuarios SET nombre = %s WHERE email = %s",
                    (nuevo_nombre, email),
                )
                actualizado = cursor.rowcount > 0
            conexion.commit()
            return actualizado
        except Exception:
            conexion.rollback()
            logging.exception("Error al actualizar usuario")
            raise

    def eliminar(self, email):
        conexion = self._obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                cursor.execute("DELETE FROM usuarios WHERE email = %s", (email,))
                eliminado = cursor.rowcount > 0
            conexion.commit()
            return eliminado
        except Exception:
            conexion.rollback()
            logging.exception("Error al eliminar usuario")
            raise
