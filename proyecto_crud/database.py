import logging
from threading import Lock

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
        self._engine_lock = Lock()

    @property
    def sesion(self) -> Session:
        if self._sesion is None:
            raise RuntimeError("Primero debes llamar a conectar()")
        return self._sesion

    def _obtener_engine(self) -> Engine:
        with self._engine_lock:
            if self.engine is None:
                configuracion = obtener_configuracion_bd()
                url = URL.create(
                    drivername="mysql+mysqlconnector",
                    username=configuracion["user"],
                    password=configuracion["pass"],
                    host=configuracion["host"],
                    port=configuracion["port"],
                    database=configuracion["database"],
                )
                self.engine = create_engine(url, pool_pre_ping=True)
            return self.engine
    # Crea una sesión nueva de SQLAlchemy para cada petición.
    def nueva_sesion(self) -> Session:
        return Session(self._obtener_engine(), expire_on_commit=False)
    # Prueba la conexión a MySQL con un SELECT 1 antes de usarla.
    def conectar(self):
        try:
            engine = self._obtener_engine()
            with engine.connect() as conexion:
                conexion.execute(text("SELECT 1"))
            self._sesion = Session(engine, expire_on_commit=False)
            logging.info("Conectado a BD")
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
            logging.info("Sesión y conexiones a MySQL cerradas")
