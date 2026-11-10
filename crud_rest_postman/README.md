# CRUD REST y cliente web para PoliRestaurante

Servicio REST en Flask para consumir desde Postman. Reutiliza los modelos,
validaciones, DAO y conexión MySQL de `proyecto_crud`; no crea ni modifica el
esquema de la base de datos. Incluye también un cliente web en HTML, Bootstrap
y JavaScript que permite administrar sus nueve recursos desde Live Server.

## Preparar y ejecutar

Desde la raíz del repositorio, instala las dependencias e inicia el servidor:

```powershell
python -m pip install -r .\crud_rest_postman\requirements.txt
python .\crud_rest_postman\app.py
```

Configura las variables `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASS` y `DB_NAME`
en `proyecto_crud\.env`. Importa `proyecto_crud\mi_base_datos.sql` si todavía
no has creado las tablas. El servidor escucha en `http://127.0.0.1:5000`.

Este servidor integrado de Flask es para desarrollo local, no para producción.

## Cliente web con Live Server

1. Instala las dependencias desde la raíz del repositorio:

   ```powershell
   python -m pip install -r .\crud_rest_postman\requirements.txt
   ```

2. Configura `proyecto_crud\.env` e inicia la API desde la raíz:

   ```powershell
   python .\crud_rest_postman\app.py
   ```

3. Abre la carpeta del repositorio en VS Code y sobre
   `crud_rest_postman\cliente\index.html` selecciona **Open with Live Server**.
   Por defecto el cliente estará en `http://127.0.0.1:5500`.

También puedes abrir `crud_rest_postman\cliente\index_pedidos.html` con Live
Server para explorar el menú, seleccionar productos con sus precios y confirmar
un pedido con su total calculado automáticamente. En esa pantalla también
puedes seleccionar un pedido existente creado desde Administración para
agregarle productos; el total se recalcula con todos sus detalles, y se
completan el estado y la fecha de creación si estaban vacíos.

La API permite CORS únicamente desde `http://127.0.0.1:5500` y
`http://localhost:5500`, los orígenes locales predeterminados de Live Server.
El cliente administra usuarios, productos, meseros, administradores, personal
de cocina, mesas, pedidos, domicilios y detalles de pedido. Para relaciones
entre registros, los formularios ofrecen un selector de administradores para
productos, mesas y pedidos. En las relaciones que todavía no tienen selector,
el formulario no solicita IDs y las referencias se conservan al editar; usa la
API para asignarlas.
El panel de Administración incluye un selector de administrador predeterminado.
La selección se guarda en el navegador y se asigna a productos, mesas y pedidos
nuevos, incluidos los creados desde la pantalla del menú. Los registros
existentes no se modifican; su administrador se conserva al editarlos.
Al tener seleccionado el recurso Usuarios, su tabla consulta cambios
automáticamente cada cinco segundos mientras la pestaña está visible y no se
está editando un registro.
Bootstrap se carga desde su CDN, por lo que la interfaz requiere conexión a
Internet para los estilos.

Extensiones recomendadas para VS Code:

- **Live Server** (Ritwick Dey), para servir el HTML y recargarlo al guardar.
- **Prettier**, para formatear HTML, CSS y JavaScript.
- **HTML CSS Support**, para autocompletar clases CSS y Bootstrap.

No abras el HTML con doble clic (`file://`): el navegador bloquea los módulos
JavaScript y las solicitudes al backend en ese modo.

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
| Personal de cocina | `/api/personal_cocina` | `id_cocina` |
| Mesas | `/api/mesas` | `id_mesa` |
| Pedidos | `/api/pedidos` | `id_pedido` |
| Domicilios | `/api/domicilios` | `id_domicilio` |
| Detalles de pedido | `/api/detalles_pedido` | `id_detalle` |

Para crear un pedido con sus productos en una sola transacción, envía
`POST /api/pedidos/con-detalles` con un objeto `pedido` y una lista no vacía
`detalles`. Si falla un detalle, también se revierte la creación del pedido.
Para agregar productos a un pedido existente, envía
`POST /api/pedidos/<id_pedido>/con-detalles` con `detalles` y, opcionalmente,
`tipo_pedido` y `nombre_cliente` para completar esos datos si están vacíos.
En ambos flujos el total se calcula desde las cantidades y precios unitarios;
si faltan, se asignan el estado `Pendiente` y la fecha de creación. Crear,
editar o eliminar detalles también recalcula el total del pedido relacionado.
Al eliminar un pedido, también se eliminan sus detalles y el domicilio asociado,
si existe; los productos no se eliminan.

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
