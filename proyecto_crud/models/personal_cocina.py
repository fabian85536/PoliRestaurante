from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models.usuario import Base


class PersonalCocina(Base):
    __tablename__ = "PersonalCocina"

    id_cocina: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str | None] = mapped_column(String(255), nullable=True)
    usuario: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contrasena: Mapped[str | None] = mapped_column(String(255), nullable=True)
