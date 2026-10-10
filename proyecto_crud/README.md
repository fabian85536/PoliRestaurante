# CRUD de usuarios con MySQL

La aplicación se conecta a MySQL usando `mysql-connector-python`. Está
configurada para usar la base `restaurante` y la tabla `usuarios`, que debe
existir con las columnas `id`, `nombre` y `email`. El CRUD no crea ni modifica
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

## Tabla usada por el CRUD

El archivo SQL del proyecto define esta tabla. Confirma que hayas importado el
SQL en tu servidor MySQL y que la tabla exista dentro de `restaurante`:

```sql
CREATE TABLE usuarios (
    id INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE
) ENGINE=InnoDB;
```

La aplicación no crea automáticamente la base ni la tabla. No ejecutes el
bloque anterior si `usuarios` ya existe.

## Pruebas

Las pruebas usan una conexión simulada y no acceden al servidor MySQL:

```powershell
python -m unittest -v test_database.py
```