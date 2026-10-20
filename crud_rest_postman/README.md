# CRUD REST para PoliRestaurante

Servicio REST en Flask para consumir desde Postman. Reutiliza los modelos,
validaciones, DAO y conexión MySQL de `proyecto_crud`; no crea ni modifica el
esquema de la base de datos.

## Preparar y ejecutar

Desde la raíz del repositorio, instala las dependencias e inicia el servidor:

```powershell
python -m pip install -r .\crud_rest_postman\requirements.txt
python .\crud_rest_postman\app.py
```

Configura las variables `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASS` y `DB_NAME`
en `proyecto_crud\.env`. Importa `proyecto_crud\mi_base_datos​.sql` si todavía
no has creado las tablas. El servidor escucha en `http://127.0.0.1:5000`.

Este servidor integrado de Flask es para desarrollo local, no para producción.

## Ejemplos didácticos en memoria

`ejemplo_usuarios.py` reúne los ejemplos Flask de usuarios que aparecen en el
flujo de Postman. Utiliza una lista en memoria, separada de la base de datos y
del servicio principal. Desde la raíz del repositorio, ejecútalo con:

```powershell
.\.venv\Scripts\python.exe .\crud_rest_postman\ejemplo_usuarios.py
```

El ejemplo escucha en `http://127.0.0.1:5001`; puedes comprobar la lista con
`GET /api/usuarios` o por ID con `GET /usuario/1`. También acepta la creación
por `POST /crear` o `POST /api/usuarios`, y la actualización y eliminación
por `PUT` y `DELETE` en `/api/usuarios/<id>`. Los registros de ejemplo se
reinician cuando detienes el servidor. Esta API en memoria es para practicar;
el servicio CRUD principal continúa en el puerto 5000 y utiliza MySQL.
También puedes probar `GET /calcular?numero=25`: devuelve el entero recibido
como `resultado`, usa `0` si no envías `numero` y responde HTTP 400 si no es
un número válido. Las rutas inexistentes y los errores internos devuelven
respuestas JSON de error.

## Recursos

Todos los recursos se encuentran bajo `/api` y aceptan `GET` para listar,
`POST` para crear, `GET /<id>` para consultar, `PATCH /<id>` para actualizar
parcialmente y `DELETE /<id>` para eliminar:

| Recurso | Ruta | Identificador |
| --- | --- | --- |
| Usuarios | `/api/usuarios` | `id` |
| Productos | `/api/productos` | `id` |
| Meseros | `/api/meseros` | `id_mesero` |
| Administradores | `/api/administradores` | `id_administrador` |
| Mesas | `/api/mesas` | `id_mesa` |
| Pedidos | `/api/pedidos` | `id_pedido` |

La ruta `GET /health` comprueba que el servicio está activo. Las respuestas de
creación usan HTTP 201 y contienen el registro; las actualizaciones devuelven
HTTP 200, las eliminaciones HTTP 204, y los registros inexistentes HTTP 404.
Los errores de validación se devuelven como JSON con HTTP 400. Los campos
`contrasena` nunca se incluyen en las respuestas.

## Ejemplo con Postman

Importa `postman\PoliRestaurante.postman_collection.json` en Postman. Usa la
variable `baseUrl` de la colección o define otra con el valor
`http://127.0.0.1:5000`. Las solicitudes de creación guardan automáticamente
el identificador en la variable correspondiente.

Ejemplo: `POST http://127.0.0.1:5000/api/productos`

```json
{
  "nombre": "Jugo natural",
  "descripcion": "Jugo de mango",
  "precio": 8000,
  "disponible": true
}
```

Ejemplo: `PATCH http://127.0.0.1:5000/api/mesas/1`

```json
{
  "estado": "Ocupada"
}
```

Los usuarios se actualizan por nombre (el correo identifica el registro y no
se cambia mediante este CRUD). En una actualización parcial, los campos
omitidos conservan su valor.

## Pruebas

Las pruebas usan una base SQLite temporal, por lo que no requieren una
conexión al servidor MySQL:

```powershell
python -m unittest discover -s .\crud_rest_postman -p "test_*.py" -v
```
