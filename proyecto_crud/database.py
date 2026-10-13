import logging

import logging

#ORM
# crea la conexión de SQLAlchemy a MySQL y abre una sesión. Esa sesión es el
#canal por el que se consultan y guardan los datos.

from sqlalchemy import URL, create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from config import obtener_configuracion_bd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class Database:
    def __init__(self):
        self.engine: Engine | None = None
        self._sesion: Session | None = None

    @property
    def sesion(self) -> Session:
        if self._sesion is None:
            raise RuntimeError("Primero debes llamar a conectar()")
        return self._sesion

    def conectar(self):
        try:
            configuracion = obtener_configuracion_bd()
            url = URL.create(
                drivername="mysql+mysqlconnector",
                username=configuracion["user"],
                password=configuracion["password"],
                host=configuracion["host"],
                port=configuracion["port"],
                database=configuracion["database"],
            )
            self.engine = create_engine(url, pool_pre_ping=True)
            with self.engine.connect() as conexion:
                conexion.execute(text("SELECT 1"))
            self._sesion = Session(self.engine, expire_on_commit=False)
            print("Conectado a BD")
        except Exception:
            self.desconectar()
            logging.exception("No se pudo conectar a MySQL")
            raise

    def desconectar(self):
        habia_recursos = self._sesion is not None or self.engine is not None
        if self._sesion is not None:
            self._sesion.close()
            self._sesion = None
        if self.engine is not None:
            self.engine.dispose()
            self.engine = None
        if habia_recursos:
            logging.info("Sesi├│n y conexiones a MySQL cerradas")
