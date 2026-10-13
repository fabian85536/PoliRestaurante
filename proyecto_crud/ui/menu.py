
from typing import Literal, overload


def mostrar_menu():

    print("\n=== CRUD RESTAURANTE ===")
    print("1. Crear usuario")
    print("2. Listar usuarios")
    print("3. Buscar usuario")
    print("4. Actualizar usuario")
    print("5. Eliminar usuario")
    print("6. Crear producto")
    print("7. Listar productos")
    print("8. Buscar producto")
    print("9. Actualizar producto")
    print("10. Eliminar producto")
    print("11. Salir")
    return input("Opción: ")


def obtener_entrada(prompt):

    while True:
        valor = input(prompt).strip()
        if valor:
            return valor
        print(" Campo no puede estar vacío")


def obtener_entrada_opcional(prompt):
    return input(prompt).strip()


def obtener_entero(prompt, opcional=False, minimo=None):
    while True:
        valor = input(prompt).strip()
        if not valor and opcional:
            return None
        try:
            numero = int(valor)
        except ValueError:
            print("Ingresa un número entero válido.")
            continue
        if minimo is not None and numero < minimo:
            print(f"El valor debe ser mayor o igual a {minimo}.")
            continue
        return numero


@overload
def obtener_confirmacion(prompt: str, opcional: Literal[False] = False) -> bool:
    ...


@overload
def obtener_confirmacion(
    prompt: str, opcional: Literal[True]
) -> bool | None:
    ...


def obtener_confirmacion(prompt, opcional=False) -> bool | None:
    while True:
        valor = input(prompt).strip().lower()
        if not valor and opcional:
            return None
        if valor in ("s", "si", "sí"):
            return True
        if valor in ("n", "no"):
            return False
        print("Responde s o n.")