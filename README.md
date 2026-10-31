# PoliRestaurante

Repositorio con dos aplicaciones Python independientes para gestionar un CRUD
de restaurante. La consola y la API comparten los modelos y DAO; ambas usan
MySQL para datos persistentes.

| Aplicación | Tecnología | Persistencia | Propósito |
| --- | --- | --- | --- |
| [`proyecto_crud`](./proyecto_crud/README.md) | Python, SQLAlchemy y CLI | MySQL | CRUD de consola para las entidades del restaurante |
| [`crud_rest_postman`](./crud_rest_postman/README.md) | Flask REST y cliente HTML/Bootstrap/JavaScript | MySQL | API CRUD y cliente web local |

La API Flask reutiliza los modelos y DAO Python del CRUD de consola. La API
es el backend del cliente web y de la colección de Postman.

## Requisitos

- Python 3.10 o superior para las aplicaciones Python.
- MySQL para ejecutar los CRUD Python contra datos persistentes.
- VS Code y Live Server para abrir el cliente web.

Las pruebas usan SQLite temporal y no requieren un servidor de base de datos.

## Preparar MySQL

1. Configura tus credenciales en `proyecto_crud\.env`. Puedes partir de la
   plantilla:

   ```powershell
   Copy-Item .\proyecto_crud\.env.example .\proyecto_crud\.env
   ```

2. Importa `proyecto_crud\mi_base_datos.sql` si todavía no has creado el
   esquema.
3. Instala dependencias y sigue las instrucciones de cada aplicación.

Los archivos `.env` locales están excluidos de Git. No guardes credenciales en
el código, capturas, colecciones de Postman ni archivos versionados.

## Pruebas

Desde la raíz, crea y activa un entorno Python local, e instala las
dependencias:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r .\proyecto_crud\requirements.txt
python -m pip install -r .\crud_rest_postman\requirements.txt
```

Pruebas del CRUD Python:

```powershell
.\.venv\Scripts\python.exe -m unittest -v test_database test_producto_dao test_entidades_dao
```

Ejecuta este comando desde `proyecto_crud`.

Pruebas de la API Flask:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s . -p "test_*.py" -v
```

Ejecuta este comando desde `crud_rest_postman`.

El flujo de GitHub Actions ejecuta ambas suites Python de forma independiente
en cada push y pull request.
