# PoliRestaurante

Repositorio con dos aplicaciones para gestionar un CRUD de restaurante:
una aplicación Python de consola y un cliente web conectado a una API Flask.
Ambas usan MySQL para los datos persistentes.

| Aplicación | Tecnología | Persistencia | Propósito |
| --- | --- | --- | --- |
| [`proyecto_crud`](./proyecto_crud/README.md) | Python, SQLAlchemy y CLI | MySQL | CRUD de consola para las entidades del restaurante |
| [`crud_rest_postman`](./crud_rest_postman/README.md) | Flask REST y HTML/JavaScript | MySQL | API CRUD y cliente web local |

## Requisitos

- Python 3.10 o superior.
- MySQL para ejecutar las aplicaciones con datos persistentes.
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
3. Instala las dependencias y sigue las instrucciones de cada aplicación.

Los archivos `.env` locales están excluidos de Git. No guardes credenciales en
el código ni en archivos versionados.

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

Ejecuta este comando desde `crud_rest_postman`. Para abrir la interfaz,
inicia la API con `python .\crud_rest_postman\app.py` y abre
`crud_rest_postman\cliente\index.html` con Live Server. GitHub Actions ejecuta
ambas suites en cada push y pull request.
