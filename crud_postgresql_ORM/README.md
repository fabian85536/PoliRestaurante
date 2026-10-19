# CRUD de usuarios con PostgreSQL y SQLAlchemy ORM

Este CRUD independiente crea, consulta, actualiza y elimina usuarios usando
SQLAlchemy ORM y PostgreSQL. La tabla `usuarios` se crea si todavía no existe;
la base de datos indicada en la URL debe existir previamente.

## Instalación y ejecución

Desde esta carpeta, instala las dependencias:

```powershell
python -m pip install -r requirements.txt
```

Configura la URL de conexión en el entorno. Sustituye usuario, contraseña, host
y base de datos por los valores reales:

```powershell
$env:DATABASE_URL = "postgresql://user:pass@localhost/db"
python main.py
```

La URL de ejemplo coincide con la forma que admite
`create_engine("postgresql://user:pass@localhost/db")`. SQLAlchemy selecciona
el controlador `psycopg2` predeterminado, incluido en las dependencias. La
creación del engine valida que la URL use PostgreSQL y que el controlador esté
instalado. Al iniciar la aplicación, SQLAlchemy intenta conectarse para crear
la tabla si hace falta. No guardes credenciales reales en el código ni en el
repositorio.

## Pruebas

Las pruebas ejecutan las operaciones CRUD contra SQLite en memoria. También
comprueban que la URL de ejemplo genera un engine PostgreSQL sin conectarse a
un servidor:

```powershell
python -m unittest -v test_crud.py
```
