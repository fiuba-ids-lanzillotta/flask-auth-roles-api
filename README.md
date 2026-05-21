# Flask Auth Roles - API

> **Aviso:** este proyecto es **codigo de ejemplo** con fines didacticos. Puede contener errores, simplificaciones o decisiones de diseno discutibles. Si se usa como base para un trabajo practico u otro entregable, **debe adaptarse a las buenas practicas y consignas especificas de la materia/catedra** (estilo de codigo, manejo de errores, validaciones, tests, seguridad, persistencia, etc.).

## Motivacion

Este proyecto es un **ejemplo practico** de como construir una pequena **API REST en Flask** con autenticacion via **JWT** y control de acceso basado en **roles** (`admin` / `usuario`), usando **MySQL** como base de datos levantada con `docker-compose`.

El objetivo es servir de referencia para cualquier proyecto que necesite estructurar un backend Python con separacion clara entre **routes / services / validators / db**, hashing de passwords con **bcrypt** y autenticacion stateless con **JWT**, todo manteniendo un estilo **funcional** (sin clases, DTOs como `dict`).

Este es el backend del ejemplo integrador; el frontend que lo consume vive en el repositorio `flask-auth-roles-web`.

## Arquitectura

```
Flujo de una request autenticada:

  Frontend (Web)
       |
       |  HTTP (JSON) + header: Authorization: Bearer <jwt>
       v
  Flask API (este proyecto, puerto 5000)
       |   - decodifica el JWT
       |   - valida el rol requerido
       v
  MySQL (contenedor docker, puerto 3306)
```

## Estructura del proyecto

```
flask-auth-roles-api/
├── app.py                          # Entry point Flask (puerto 5000)
├── docker-compose.yml              # MySQL 8 + volumen + script de inicializacion
├── requirements.txt                # Dependencias Python
├── .env.example                    # Template para configurar DB y JWT
├── flask_auth_roles/
│   ├── constants.py                # Configuracion (DB, JWT, roles, codigos de error)
│   ├── db.py                       # Capa de acceso a datos (queries literales)
│   ├── utils.py                    # Validaciones, hashing bcrypt, JWT, @requiere_auth
│   ├── routes/
│   │   ├── auth.py                 # POST /register, POST /login
│   │   └── usuarios.py             # GET /me, GET/DELETE /usuarios[/<id>]
│   ├── services/
│   │   ├── auth.py                 # Logica de registro y login
│   │   └── usuarios.py             # Logica de usuarios
│   └── validators/
│       └── auth.py                 # Validacion de bodies de login y registro
└── db/
    └── init_db.sql                 # Esquema (tabla usuarios)
```

## Requisitos previos

- Python 3.10+
- **Una** de las dos opciones para correr MySQL:
  - Docker + Docker Compose (recomendado), o
  - Una instalacion local de MySQL 8

## Configuracion

### 1. Variables de entorno

Copiar `.env.example` a `.env` (los defaults ya funcionan para desarrollo local):

```bash
cp .env.example .env
```

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root
DB_NAME=auth_roles

JWT_SECRET=change-me-please
JWT_EXP_HORAS=8
```

> **Importante:** en cualquier ambiente que no sea desarrollo local, definir un `JWT_SECRET` propio y largo. Es la clave con la que se firman todos los tokens.

### 2. Base de datos MySQL

Eleg **una** de las dos opciones segun lo que tengas instalado.

#### Opcion A: con Docker (recomendado)

`docker-compose.yml` levanta MySQL 8 y monta `db/init_db.sql` como script de inicializacion, creando la tabla `usuarios` automaticamente la **primera** vez:

```bash
docker compose up -d
```

Verificar que el contenedor este listo (puede tardar unos segundos):

```bash
docker compose logs -f mysql
# Buscar la linea: "ready for connections"
```

Apagar el contenedor manteniendo los datos en el volumen:

```bash
docker compose down
```

Apagar y **borrar** los datos (la proxima vez se vuelve a correr `init_db.sql`):

```bash
docker compose down -v
```

#### Opcion B: con MySQL instalado localmente

Si ya tenes MySQL 8 corriendo en tu maquina (puerto `3306` por default):

1. Crear la base de datos y cargar el esquema:

   ```bash
   # Linux / macOS / WSL
   mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS auth_roles;"
   mysql -u root -p auth_roles < db/init_db.sql
   ```

   ```powershell
   # Windows PowerShell
   mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS auth_roles;"
   Get-Content db\init_db.sql | mysql -u root -p auth_roles
   ```

2. Verificar que la tabla se haya creado:

   ```bash
   mysql -u root -p -e "USE auth_roles; SHOW TABLES;"
   ```

   Deberias ver: `usuarios`.

3. Si tu usuario, password, puerto o nombre de base no coinciden con los defaults, actualiza el `.env` antes de levantar la API.

### 3. Entorno virtual, instalacion y ejecucion

El proyecto incluye scripts de setup que crean el entorno virtual, instalan las dependencias y levantan la API.

**Con virtualenv:**

```bash
# Windows
setup_virtualenv.bat

# Linux / macOS
chmod +x setup_virtualenv.sh
./setup_virtualenv.sh
```

**Con pipenv:**

```bash
# Windows
setup_pipenv.bat

# Linux / macOS
chmod +x setup_pipenv.sh
./setup_pipenv.sh
```

Una vez iniciada, la API estara disponible en `http://localhost:5000/flask_auth_roles_api`.

### 4. Crear el primer usuario admin

La tabla `usuarios` arranca vacia (no incluimos seed para evitar passwords hardcodeados). Para crear el primer admin, hace un `POST` al endpoint de registro indicando `rol: admin`:

```bash
curl -X POST http://localhost:5000/flask_auth_roles_api/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@admin.com","nombre":"Admin","password":"admin123","rol":"admin"}'
```

> En un sistema real, el campo `rol` **nunca** se aceptaria desde el body de `/register`. En este ejemplo lo dejamos abierto para simplificar el bootstrapping; en un caso real lo manejarias con un script de seed o un endpoint protegido por admin.

## Endpoints

Todos los endpoints estan bajo el prefijo `/flask_auth_roles_api`. Las respuestas son JSON; los errores siguen el formato:

```json
{
    "errors": [
        {
            "code": "<codigo>",
            "message": "<mensaje breve>",
            "level": "error",
            "description": "<descripcion detallada>"
        }
    ]
}
```

| Metodo | Endpoint                | Auth        | Descripcion                                |
|--------|-------------------------|-------------|--------------------------------------------|
| POST   | `/register`             | Publico     | Registra un usuario nuevo                  |
| POST   | `/login`                | Publico     | Devuelve `{token, usuario}`                |
| GET    | `/me`                   | Autenticado | Datos del usuario logueado                 |
| GET    | `/usuarios`             | Admin       | Lista todos los usuarios                   |
| GET    | `/usuarios/<id>`        | Admin       | Detalle de un usuario por id               |
| DELETE | `/usuarios/<id>`        | Admin       | Elimina un usuario                         |

Para los endpoints autenticados, enviar el header:

```
Authorization: Bearer <token>
```

### `POST /register`

Crea un nuevo usuario.

**Headers**: `Content-Type: application/json`

**Body**:

| Campo      | Tipo   | Requerido | Descripcion                                         |
|------------|--------|-----------|-----------------------------------------------------|
| `email`    | string | si        | Email valido y unico                                |
| `nombre`   | string | si        | Nombre del usuario (1-100 caracteres)               |
| `password` | string | si        | Password en texto plano (6-64 caracteres)           |
| `rol`      | string | no        | `"admin"` o `"usuario"`. Default: `"usuario"`       |

```bash
curl -X POST http://localhost:5000/flask_auth_roles_api/register \
  -H "Content-Type: application/json" \
  -d '{"email":"jperez@mail.com","nombre":"Juan Perez","password":"secret123"}'
```

Respuesta `201 Created`:

```json
{ "id": 2, "email": "jperez@mail.com", "nombre": "Juan Perez", "rol": "usuario" }
```

Posibles errores:

- `400 Bad Request`: body invalido o campos con formato incorrecto (la respuesta puede incluir varios errores acumulados en `errors[]`).
- `409 Conflict`: ya existe un usuario con ese email.

### `POST /login`

Valida las credenciales y devuelve un JWT.

**Body**: `{ "email": "...", "password": "..." }`

```bash
curl -X POST http://localhost:5000/flask_auth_roles_api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@admin.com","password":"admin123"}'
```

Respuesta `200 OK`:

```json
{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "usuario": { "id": 1, "email": "admin@admin.com", "nombre": "Admin", "rol": "admin" }
}
```

Posibles errores:

- `400 Bad Request`: body invalido.
- `401 Unauthorized`: credenciales invalidas.

### `GET /me`

Retorna el usuario asociado al token enviado.

```bash
curl http://localhost:5000/flask_auth_roles_api/me \
  -H "Authorization: Bearer <token>"
```

Respuesta `200 OK`:

```json
{ "id": 1, "email": "admin@admin.com", "nombre": "Admin", "rol": "admin" }
```

Posibles errores: `401` (token faltante / invalido / expirado), `404` (usuario eliminado).

### `GET /usuarios` *(solo admin)*

Lista todos los usuarios.

```bash
curl http://localhost:5000/flask_auth_roles_api/usuarios \
  -H "Authorization: Bearer <token>"
```

Respuesta `200 OK`:

```json
[
    { "id": 1, "email": "admin@admin.com",  "nombre": "Admin",      "rol": "admin" },
    { "id": 2, "email": "jperez@mail.com",  "nombre": "Juan Perez", "rol": "usuario" }
]
```

Si no hay usuarios, devuelve `204 No Content`. Posibles errores: `401`, `403` (no es admin).

### `GET /usuarios/<id>` *(solo admin)*

Detalle de un usuario por id.

Posibles errores: `400` (id invalido), `401`, `403`, `404`.

### `DELETE /usuarios/<id>` *(solo admin)*

Elimina un usuario.

Respuesta `204 No Content`. Posibles errores: `400`, `401`, `403`, `404`.

## Patron de queries literales

Este proyecto usa SQLAlchemy **sin ORM**, ejecutando SQL directamente con `text()`:

```python
from sqlalchemy import create_engine, text

motor = create_engine(DB_URL)

# SELECT
with motor.connect() as conexion:
    resultado = conexion.execute(text(sql), {'email': 'admin@admin.com'})

# INSERT/UPDATE/DELETE (con commit automatico)
with motor.begin() as conexion:
    resultado = conexion.execute(text(sql), parametros)
```

Ver `flask_auth_roles/db.py` para todos los ejemplos.

## Patron de autenticacion

- El **password** se hashea con `bcrypt` antes de guardarlo (`utils.hashear_password`).
- En el login se compara el password recibido contra el hash con `bcrypt.checkpw` (`utils.verificar_password`).
- Si las credenciales son validas, se genera un JWT (`utils.generar_token`) con:
  - `sub`: id del usuario
  - `rol`: rol del usuario
  - `exp`: expiracion en `JWT_EXP_HORAS` horas
- Los endpoints protegidos usan el decorador `@requiere_auth(rol=...)` de `utils.py`, que:
  1. extrae el token del header `Authorization: Bearer <token>`,
  2. lo decodifica y valida con el `JWT_SECRET`,
  3. opcionalmente verifica que el `rol` coincida con el requerido,
  4. inyecta el payload en `request.usuario_actual` para que la vista lo use.

Toda la auth es **stateless**: la API no guarda sesiones; cada request se valida con el JWT.
