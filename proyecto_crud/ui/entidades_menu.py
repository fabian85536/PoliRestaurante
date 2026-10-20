from getpass import getpass

from sqlalchemy.exc import SQLAlchemyError

from ui.menu import obtener_entero, obtener_entrada, obtener_entrada_opcional

MESERO_CAMPOS = (
    ("nombre", "Nombre", "texto", True, None),
    ("usuario", "Usuario", "texto", True, None),
    ("contrasena", "Contraseña", "secreto", True, None),
)
ADMINISTRADOR_CAMPOS = MESERO_CAMPOS
MESA_CAMPOS = (
    ("numero", "Número de mesa", "entero", True, 1),
    ("estado", "Estado", "texto", True, None),
    ("id_administrador", "ID del administrador (opcional)", "entero", False, 1),
)
PEDIDO_CAMPOS = (
    ("id_mesero", "ID del mesero (opcional)", "entero", False, 1),
    ("id_cocina", "ID del personal de cocina (opcional)", "entero", False, 1),
    ("id_administrador", "ID del administrador (opcional)", "entero", False, 1),
    ("id_mesa", "ID de la mesa (opcional)", "entero", False, 1),
    ("tipo_pedido", "Tipo de pedido", "opcional", False, None),
    ("nombre_cliente", "Nombre del cliente", "opcional", False, None),
    ("estado", "Estado", "opcional", False, None),
    ("total", "Total", "entero", False, 0),
    ("metodo_pago", "Método de pago", "opcional", False, None),
    ("fecha_creacion", "Fecha de creación", "opcional", False, None),
    ("fecha_cierre", "Fecha de cierre", "opcional", False, None),
)


def _leer_datos(campos, registro=None):
    datos = {}
    actualizacion = registro is not None
    for nombre, etiqueta, tipo, requerido, minimo in campos:
        valor_actual = getattr(registro, nombre) if actualizacion else None
        etiqueta_prompt = etiqueta
        if actualizacion:
            etiqueta_prompt = f"{etiqueta} [{valor_actual or ''}] (vacío conserva)"
        prompt = f"{etiqueta_prompt}: "

        if tipo == "entero":
            valor = obtener_entero(
                prompt,
                opcional=actualizacion or not requerido,
                minimo=minimo,
            )
        elif tipo == "secreto":
            valor = getpass(prompt)
            if actualizacion and not valor:
                valor = None
            elif not actualizacion and not valor.strip():
                print("El campo Contraseña es obligatorio.")
                valor = _leer_secreto_obligatorio(prompt)
        elif tipo == "opcional" or actualizacion:
            valor = obtener_entrada_opcional(prompt)
            valor = valor or None
        else:
            valor = obtener_entrada(prompt)

        if valor is not None:
            datos[nombre] = valor
    return datos


def _leer_secreto_obligatorio(prompt):
    while True:
        valor = getpass(prompt)
        if valor.strip():
            return valor
        print("El campo Contraseña es obligatorio.")


def ejecutar_menu_entidad(
    dao,
    nombre,
    plural,
    campos,
    crear,
    listar,
):
    while True:
        print(f"\n=== CRUD {nombre.upper()} ===")
        print(f"1. Crear {nombre.lower()}")
        print(f"2. Listar {plural.lower()}")
        print(f"3. Buscar {nombre.lower()}")
        print(f"4. Actualizar {nombre.lower()}")
        print(f"5. Eliminar {nombre.lower()}")
        print("6. Volver")
        opcion = input("Opción: ").strip()

        try:
            if opcion == "1":
                registro_id = crear(**_leer_datos(campos))
                print(f"{nombre} creado con ID {registro_id}")
            elif opcion == "2":
                registros = listar()
                if not registros:
                    print(f"No hay {plural.lower()} registrados.")
                for registro in registros:
                    print(
                        " | ".join(
                            f"{clave}: {valor}"
                            for clave, valor in registro.to_dict().items()
                        )
                    )
            elif opcion == "3":
                registro_id = obtener_entero(f"ID del {nombre.lower()}: ", minimo=1)
                registro = dao.obtener_por_id(registro_id)
                if registro is None:
                    print(f"No se encontró {nombre.lower()}.")
                else:
                    print(
                        " | ".join(
                            f"{clave}: {valor}"
                            for clave, valor in registro.to_dict().items()
                        )
                    )
            elif opcion == "4":
                registro_id = obtener_entero(
                    f"ID del {nombre.lower()} a actualizar: ", minimo=1
                )
                registro = dao.obtener_por_id(registro_id)
                if registro is None:
                    print(f"No se encontró {nombre.lower()}.")
                    continue
                datos = _leer_datos(campos, registro)
                if not datos:
                    print("No se ingresaron cambios.")
                elif dao.actualizar(registro_id, **datos):
                    print(f"{nombre} actualizado.")
                else:
                    print(f"No se encontró {nombre.lower()}.")
            elif opcion == "5":
                registro_id = obtener_entero(
                    f"ID del {nombre.lower()} a eliminar: ", minimo=1
                )
                if dao.eliminar(registro_id):
                    print(f"{nombre} eliminado.")
                else:
                    print(f"No se encontró {nombre.lower()}.")
            elif opcion == "6":
                return
            else:
                print("Opción inválida.")
        except ValueError as error:
            print(f"No se pudo procesar {nombre.lower()}: {error}")
        except SQLAlchemyError as error:
            print(f"Error de base de datos al procesar {nombre.lower()}: {error}")
