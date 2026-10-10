import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")


def obtener_configuracion_bd():
    variables = {
        "host": "DB_HOST",
        "user": "DB_USER",
        "password": "DB_PASS",
        "database": "DB_NAME",
    }
    configuracion = {}
    for parametro, variable in variables.items():
        valor = os.getenv(variable)
        if not valor:
            raise ValueError(f"Falta configurar {variable} en el archivo .env")
        configuracion[parametro] = valor

    try:
        configuracion["port"] = int(os.getenv("DB_PORT", "3306"))
    except ValueError as error:
        raise ValueError("DB_PORT debe ser un número entero") from error

    return configuracion