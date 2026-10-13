if __name__ == "__main__":
    print("INICIANDO PRUEBA DE PRODUCTOS")
    from database import Database

    db = Database()
    try:
        print("Conectando a MySQL...")
        db.conectar()
        print("Conexión exitosa.")
        print("Esta prueba requiere la configuración de la base de datos .env")
        print("Y una tabla Producto con las columnas esperadas por el proyecto.")
    except Exception as exc:
        print(f"Error al ejecutar la prueba: {exc}")
    finally:
        db.desconectar()
