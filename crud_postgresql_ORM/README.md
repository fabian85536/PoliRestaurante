# CRUD REST con Spring Boot, Spring Data JPA y PostgreSQL

Este módulo es una aplicación Java/Maven independiente. Usa
`spring-boot-starter-data-jpa` para mapear `Usuario` y persistirlo mediante
Spring Data JPA. La API expone operaciones CRUD en `/api/usuarios`.

## Requisitos

- JDK 17 o superior
- Maven 3.6 o superior
- PostgreSQL con la base de datos creada

## Ejecutar

Desde esta carpeta, configura la conexión y arranca Spring Boot:

```powershell
$env:DATABASE_URL = "jdbc:postgresql://localhost:5432/db"
$env:DATABASE_USERNAME = "user"
$env:DATABASE_PASSWORD = "pass"
mvn spring-boot:run
```

También se pueden dejar las variables sin configurar para usar los valores
locales predeterminados en `application.properties`. La base de datos `db`
debe existir; Hibernate crea o actualiza la tabla `usuarios`.

## Endpoints

| Método | Ruta | Acción |
|---|---|---|
| `POST` | `/api/usuarios` | Crear usuario |
| `GET` | `/api/usuarios` | Listar usuarios |
| `GET` | `/api/usuarios/{id}` | Buscar usuario |
| `PUT` | `/api/usuarios/{id}` | Actualizar usuario |
| `DELETE` | `/api/usuarios/{id}` | Eliminar usuario |

Ejemplo de cuerpo JSON para crear o actualizar:

```json
{
  "nombre": "Ana",
  "email": "ana@example.com"
}
```

La API valida nombre y email, responde `409 Conflict` si el email ya está
registrado y `404 Not Found` si el ID solicitado no existe.

## Pruebas

Las pruebas de integración usan H2 en memoria, por lo que no requieren un
servidor PostgreSQL:

```powershell
mvn test
```
