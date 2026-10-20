from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models.usuario import Base


class PersonalCocina(Base):
    __tablename__ = "PersonalCocina"

    id_cocina: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str | None] = mapped_column(String(255), nullable=True)
    usuario: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contrasena: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def validar(self):
        for campo in ("nombre", "usuario", "contrasena"):
            valor = getattr(self, campo)
            if valor is None or not valor.strip():
                raise ValueError(f"El campo {campo} es obligatorio.")
            setattr(self, campo, valor.strip())

    def actualizar(self, nombre=None, usuario=None, contrasena=None):
        for campo, valor in (
            ("nombre", nombre),
            ("usuario", usuario),
            ("contrasena", contrasena),
        ):
            if valor is not None:
                setattr(self, campo, valor.strip())
        self.validar()

    def to_dict(self):
        return {
            "id_cocina": self.id_cocina,
            "nombre": self.nombre,
            "usuario": self.usuario,
        }
