import logging

import mysql.connector
from config import obtener_configuracion_bd

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