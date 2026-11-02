from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from models.pedido import Pedido
from models.usuario import Base
from models.Producto import Producto


class DetallePedido(Base):
    __tablename__ = "DetallePedido"

    id_detalle: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_pedido: Mapped[int | None] = mapped_column(
        ForeignKey("Pedido.id_pedido"), nullable=True
    )
    id_producto: Mapped[int | None] = mapped_column(
        ForeignKey("Producto.id_producto"), nullable=True
    )
    cantidad: Mapped[int | None] = mapped_column(Integer, nullable=True)
    precio_unitario: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notas: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def validar(self):
        for campo in ("cantidad", "precio_unitario"):
            valor = getattr(self, campo)
            if valor is not None:
                valor = int(valor)
                if valor < 0 or (campo == "cantidad" and valor == 0):
                    raise ValueError(
                        "La cantidad debe ser positiva y el precio unitario "
                        "no puede ser negativo."
                    )
                setattr(self, campo, valor)
        if self.notas is not None:
            self.notas = self.notas.strip()

    def actualizar(self, **datos):
        for campo, valor in datos.items():
            if valor is not None:
                if campo in {"id_pedido", "id_producto", "cantidad", "precio_unitario"}:
                    valor = int(valor)
                else:
                    valor = valor.strip()
                setattr(self, campo, valor)
        self.validar()

    def to_dict(self):
        return {
            "id_detalle": self.id_detalle,
            "id_pedido": self.id_pedido,
            "id_producto": self.id_producto,
            "cantidad": self.cantidad,
            "precio_unitario": self.precio_unitario,
            "notas": self.notas,
        }
