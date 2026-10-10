import mysql.connector

from database import Database
from ui.menu import mostrar_menu, obtener_entrada

db = Database()

try:
    db.conectar()
    while True:
        opcion = mostrar_menu()
        if opcion == "1":
            nombre = obtener_entrada("Nombre: ")
            email = obtener_entrada("Email: ")
            usuario_id = db.crear_usuario(nombre, email)
            print(f"Usuario creado con ID {usuario_id}")
        elif opcion == "2":
            for usuario in db.obtener_usuarios():
                print(
                    f"ID: {usuario['id']} | Nombre: {usuario['nombre']} "
                    f"| Email: {usuario['email']}"
                )
        elif opcion == "3":
            email = obtener_entrada("Email a buscar: ")
            usuario = db.obtener_por_email(email)
            if usuario:
                print(usuario)
            else:
                print("No se encontró ese usuario")
        elif opcion == "4":
            email = obtener_entrada("Email del usuario: ")
            nuevo_nombre = obtener_entrada("Nuevo nombre: ")
            if db.actualizar(email, nuevo_nombre):
                print("Usuario actualizado")
            else:
                print("No se encontró ese usuario")
        elif opcion == "5":
            email = obtener_entrada("Email del usuario a eliminar: ")
            if db.eliminar(email):
                print("Usuario eliminado")
            else:
                print("No se encontró ese usuario")
        elif opcion == "6":
            break
        else:
            print("Opción inválida")
except (mysql.connector.Error, RuntimeError, ValueError) as error:
    print(f"Error: {error}")
finally:
    db.desconectar()