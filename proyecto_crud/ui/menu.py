def mostrar_menu():

    print("\n=== CRUD USUARIOS ===")
    print("1. Crear usuario")
    print("2. Listar usuarios")
    print("3. Buscar usuario")
    print("4. Actualizar usuario")
    print("5. Eliminar usuario")
    print("6. Salir")
    return input("Opción: ")

def obtener_entrada(prompt):

    while True:
        valor = input(prompt).strip()
        if valor:
            return valor
        print("❌ Campo no puede estar vacío")