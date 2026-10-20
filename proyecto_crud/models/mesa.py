from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from models.administrador import Administrador
from models.usuario import Base


class Mesa(Base):
    __tablename__ = "Mesa"

    id_mesa: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    numero: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estado: Mapped[str | None] = mapped_column(String(255), nullable=True)
    id_administrador: Mapped[int | None] = mapped_column(
        ForeignKey("Administrador.id_administrador"), nullable=True
    )

    def validar(self):
        if self.numero is not None:
            self.numero = int(self.numero)
            if self.numero < 1:
                raise ValueError("El número de mesa debe ser mayor que cero.")
        if self.estado is not None:
            self.estado = self.estado.strip()

    def actualizar(self, numero=None, estado=None, id_administrador=None):
        if numero is not None:
            self.numero = int(numero)
        if estado is not None:
            self.estado = estado.strip()
        if id_administrador is not None:
            self.id_administrador = int(id_administrador)
        self.validar()

    def to_dict(self):
        return {
            "id_mesa": self.id_mesa,
            "numero": self.numero,
            "estado": self.estado,
            "id_administrador": self.id_administrador,
        }
