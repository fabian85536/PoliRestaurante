# CRUD de restaurante con MySQL

La aplicación usa SQLAlchemy ORM con MySQL (`mysql-connector-python`) para
mapear los modelos a las tablas de `restaurante`. Incluye CRUD para usuarios,
productos, meseros, administradores, mesas y pedidos. El ORM no crea ni modifica
la estructura de la base de datos.

## Configuración

1. Instala las dependencias desde esta carpeta:

   ```powershell
   python -m pip install -r requirements.txt
   ```

2. Copia `.env.example` como `.env` y completa los datos de conexión de tu
   servidor MySQL. En el esquema compartido, el nombre de base de datos es
   `restaurante`:

   ```powershell
   Copy-Item .env.example .env
   ```

3. Inicia el CRUD:

   ```powershell
   python main.py
   ```

No compartas ni subas el archivo `.env`; contiene las credenciales de acceso.

## Tablas usadas por el CRUD

Importa `mi_base_datos.sql` en tu servidor MySQL para crear el esquema esperado.
Las operaciones nuevas usan las tablas `Mesero`, `Administrador`, `Mesa` y
`Pedido`, incluyendo las referencias a meseros, personal de cocina,
administradores y mesas ya definidas en el SQL del proyecto. El CRUD no crea
automáticamente la base ni las tablas.

En el menú principal, las opciones 12 a 15 abren los CRUD de meseros,
administradores, mesas y pedidos, respectivamente. Las contraseñas no se
muestran al listar registros.

## Pruebas

Las pruebas usan una conexión simulada y no acceden al servidor MySQL:

```powershell
python -m unittest -v test_database.py
```

Prueba también los productos y las cuatro entidades nuevas:

```powershell
python -m unittest -v test_producto_dao.py test_entidades_dao.py
```