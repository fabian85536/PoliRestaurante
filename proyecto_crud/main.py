#ORM
#conecta métodos con las opciones del menú.
from sqlalchemy.exc import SQLAlchemyError

from database import Database
from models.administrador_DAO import AdministradorDAO
from models.mesa_DAO import MesaDAO
from models.mesero_DAO import MeseroDAO
from models.pedido_DAO import PedidoDAO
from models.personal_cocina_DAO import PersonalCocinaDAO
from models.producto_DAO import ProductoDAO
from models.usuario_DAO import UsuarioDAO
from ui.entidades_menu import (
    ADMINISTRADOR_CAMPOS,
    MESA_CAMPOS,
    MESERO_CAMPOS,
    PEDIDO_CAMPOS,
    PERSONAL_COCINA_CAMPOS,
    ejecutar_menu_entidad,
)
from ui.menu import (
    mostrar_menu,
    obtener_confirmacion,
    obtener_entero,
    obtener_entrada,
    obtener_entrada_opcional,
)


def obtener_id_catalogo(prompt, ids_validos):
    if not ids_validos:
        print("No hay registros disponibles; se guardará sin asignar uno.")
        return None
    while True:
        valor = obtener_entrada_opcional(prompt)
        if not valor:
            return None
        try:
            id_registro = int(valor)
        except ValueError:
            print("Ingresa un ID numérico de la lista o deja el campo vacío.")
            continue
        if id_registro in ids_validos:
            return id_registro
        print("Ese ID no está en la lista. Elige uno disponible o deja el campo vacío.")


db = Database()

try:
    db.conectar()
    usuario_dao = UsuarioDAO(db.sesion)
    producto_dao = ProductoDAO(db.sesion)
    mesero_dao = MeseroDAO(db.sesion)
    administrador_dao = AdministradorDAO(db.sesion)
    mesa_dao = MesaDAO(db.sesion)
    pedido_dao = PedidoDAO(db.sesion)
    personal_cocina_dao = PersonalCocinaDAO(db.sesion)
    while True:
        opcion = mostrar_menu()
        if opcion == "1":
            nombre = obtener_entrada("Nombre: ")
            email = obtener_entrada("Email: ")
            usuario_id = usuario_dao.crear_usuario(nombre, email)
            print(f"Usuario creado con ID {usuario_id}")
        elif opcion == "2":
            for usuario in usuario_dao.obtener_usuarios():
                print(
                    f"ID: {usuario.id} | Nombre: {usuario.nombre} "
                    f"| Email: {usuario.email}"
                )
        elif opcion == "3":
            email = obtener_entrada("Email a buscar: ")
            usuario = usuario_dao.obtener_por_email(email)
            if usuario:
                print(
                    f"ID: {usuario.id} | Nombre: {usuario.nombre} "
                    f"| Email: {usuario.email}"
                )
            else:
                print("No se encontró ese usuario")
        elif opcion == "4":
            email = obtener_entrada("Email del usuario: ")
            nuevo_nombre = obtener_entrada("Nuevo nombre: ")
            if usuario_dao.actualizar(email, nuevo_nombre):
                print("Usuario actualizado")
            else:
                print("No se encontró ese usuario")
        elif opcion == "5":
            email = obtener_entrada("Email del usuario a eliminar: ")
            if usuario_dao.eliminar(email):
                print("Usuario eliminado")
            else:
                print("No se encontró ese usuario")
        elif opcion == "6":
            nombre = obtener_entrada("Nombre del producto: ")
            descripcion = obtener_entrada_opcional("Descripción (opcional): ")
            precio = obtener_entero("Precio (entero): ", minimo=1)
            categorias = producto_dao.obtener_categorias()
            administradores = producto_dao.obtener_administradores()
            print("Categorías disponibles:")
            for categoria in categorias:
                print(f"  {categoria.id_categoria}: {categoria.nombre or 'Sin nombre'}")
            print("Administradores disponibles:")
            for administrador in administradores:
                print(
                    f"  {administrador.id_administrador}: "
                    f"{administrador.nombre or 'Sin nombre'}"
                )
            id_categoria = obtener_id_catalogo(
                "ID de categoría (opcional): ",
                [categoria.id_categoria for categoria in categorias],
            )
            id_administrador = obtener_id_catalogo(
                "ID de administrador (opcional): ",
                [administrador.id_administrador for administrador in administradores],
            )
            disponible = obtener_confirmacion("¿Está disponible? (s/n): ")
            try:
                producto_id = producto_dao.crear_producto(
                    nombre,
                    descripcion,
                    precio,
                    id_categoria,
                    id_administrador,
                    disponible,
                )
                print(f"Producto creado con ID {producto_id}")
            except ValueError as error:
                print(f"No se pudo crear el producto: {error}")
        elif opcion == "7":
            for producto in producto_dao.obtener_productos():
                estado = "Sí" if producto.disponible else "No"
                print(
                    f"ID: {producto.id_producto} | Nombre: {producto.nombre} "
                    f"| Descripción: {producto.descripcion} "
                    f"| Precio: {producto.precio} "
                    f"| Categoría: {producto.id_categoria} "
                    f"| Disponible: {estado}"
                )
        elif opcion == "8":
            producto_id = obtener_entero("ID del producto a buscar: ", minimo=1)
            producto = producto_dao.obtener_por_id(producto_id)
            if producto:
                print(
                    f"ID: {producto.id_producto} | Nombre: {producto.nombre} "
                    f"| Descripción: {producto.descripcion} "
                    f"| Precio: {producto.precio} "
                    f"| Categoría: {producto.id_categoria} "
                    f"| Disponible: {'Sí' if producto.disponible else 'No'}"
                )
            else:
                print("No se encontró ese producto")
        elif opcion == "9":
            producto_id = obtener_entero(
                "ID del producto a actualizar: ", minimo=1
            )
            producto = producto_dao.obtener_por_id(producto_id)
            if producto is None:
                print("No se encontró ese producto")
                continue
            nombre = obtener_entrada_opcional(
                f"Nuevo nombre [{producto.nombre}]: "
            )
            descripcion = obtener_entrada_opcional(
                f"Nueva descripción [{producto.descripcion}]: "
            )
            precio = obtener_entero(
                f"Nuevo precio [{producto.precio}]: ", opcional=True, minimo=1
            )
            categorias = producto_dao.obtener_categorias()
            administradores = producto_dao.obtener_administradores()
            print("Categorías disponibles:")
            for categoria in categorias:
                print(f"  {categoria.id_categoria}: {categoria.nombre or 'Sin nombre'}")
            print("Administradores disponibles:")
            for administrador in administradores:
                print(
                    f"  {administrador.id_administrador}: "
                    f"{administrador.nombre or 'Sin nombre'}"
                )
            id_categoria = obtener_id_catalogo(
                f"ID de categoría [{producto.id_categoria or ''}] (vacío conserva): ",
                [categoria.id_categoria for categoria in categorias],
            )
            id_administrador = obtener_id_catalogo(
                f"ID de administrador [{producto.id_administrador or ''}] "
                "(vacío conserva): ",
                [administrador.id_administrador for administrador in administradores],
            )
            disponible = obtener_confirmacion(
                f"¿Disponible? (s/n) [{'s' if producto.disponible else 'n'}]: ",
                opcional=True,
            )
            try:
                if producto_dao.actualizar(
                    producto_id,
                    nombre or None,
                    descripcion or None,
                    precio,
                    id_categoria,
                    id_administrador,
                    disponible,
                ):
                    print("Producto actualizado")
                else:
                    print("No se encontró ese producto")
            except ValueError as error:
                print(f"No se pudo actualizar el producto: {error}")
        elif opcion == "10":
            producto_id = obtener_entero(
                "ID del producto a eliminar: ", minimo=1
            )
            if producto_dao.eliminar(producto_id):
                print("Producto eliminado")
            else:
                print("No se encontró ese producto")
        elif opcion == "11":
            break
        elif opcion == "12":
            ejecutar_menu_entidad(
                mesero_dao,
                "Mesero",
                "Meseros",
                MESERO_CAMPOS,
                mesero_dao.crear_mesero,
                mesero_dao.obtener_meseros,
            )
        elif opcion == "13":
            ejecutar_menu_entidad(
                administrador_dao,
                "Administrador",
                "Administradores",
                ADMINISTRADOR_CAMPOS,
                administrador_dao.crear_administrador,
                administrador_dao.obtener_administradores,
            )
        elif opcion == "14":
            ejecutar_menu_entidad(
                mesa_dao,
                "Mesa",
                "Mesas",
                MESA_CAMPOS,
                mesa_dao.crear_mesa,
                mesa_dao.obtener_mesas,
            )
        elif opcion == "15":
            ejecutar_menu_entidad(
                pedido_dao,
                "Pedido",
                "Pedidos",
                PEDIDO_CAMPOS,
                pedido_dao.crear_pedido,
                pedido_dao.obtener_pedidos,
            )
        elif opcion == "16":
            ejecutar_menu_entidad(
                personal_cocina_dao,
                "Personal de cocina",
                "Personal de cocina",
                PERSONAL_COCINA_CAMPOS,
                personal_cocina_dao.crear_personal_cocina,
                personal_cocina_dao.obtener_personal_cocina,
            )
        else:
            print("Opción inválida")
except (SQLAlchemyError, RuntimeError, ValueError) as error:
    print(f"Error: {error}")
finally:
    db.desconectar()