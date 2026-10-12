
class Producto:
    def __init__(
        self,
        nombre,
        descripcion,
        precio,
        categoria,
        disponible=True,
        id=None
    ):
        self.id = id
        self.nombre = nombre.strip()
        self.descripcion = descripcion.strip()
        self.precio = float(precio)
        self.categoria = categoria.strip()
        self.disponible = bool(disponible)

        self.validar()

    def validar(self):
        if not self.nombre:
            raise ValueError("El nombre del producto es obligatorio.")

        if self.precio <= 0:
            raise ValueError("El precio debe ser mayor que cero.")

        if not self.categoria:
            raise ValueError("La categoría del producto es obligatoria.")

    def actualizar(
        self,
        nombre=None,
        descripcion=None,
        precio=None,
        categoria=None,
        disponible=None
    ):
        if nombre is not None:
            self.nombre = nombre.strip()

        if descripcion is not None:
            self.descripcion = descripcion.strip()

        if precio is not None:
            self.precio = float(precio)

        if categoria is not None:
            self.categoria = categoria.strip()

        if disponible is not None:
            self.disponible = bool(disponible)

        self.validar()

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "precio": self.precio,
            "categoria": self.categoria,
            "disponible": self.disponible
        }
