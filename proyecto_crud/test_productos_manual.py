
from database import Database

print("INICIANDO PRUEBA DE PRODUCTOS")

db = Database()

try:
    print("Conectando a MySQL...")
    db.conectar()
    print("Conexión exitosa.")

    producto_id = db.crear_producto(
        nombre="Hamburguesa clásica",
        descripcion="Carne, queso y vegetales",
        precio=18000,
        categoria="Hamburguesas",
        disponible=True,
    )

    print("Producto creado:", producto_id)
    print("Productos registrados:", db.obtener_productos())

finally:
    db.desconectar()

