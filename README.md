# Flask Auth Roles - API

> **Aviso:** este proyecto es **codigo de ejemplo** con fines didacticos. Puede contener errores, simplificaciones o decisiones de diseno discutibles. Si se usa como base para un trabajo practico u otro entregable, **debe adaptarse a las buenas practicas y consignas especificas de la materia/catedra** (estilo de codigo, manejo de errores, validaciones, tests, seguridad, persistencia, etc.).

## Motivacion

Este proyecto es un **ejemplo practico** de como construir una pequena **API REST en Flask** con autenticacion via **JWT** y control de acceso basado en **roles** (`admin` / `usuario`), usando **MySQL** como base de datos levantada con `docker-compose`.

El objetivo es servir de referencia para cualquier proyecto que necesite estructurar un backend Python con separacion clara entre **routes / services / validators / db**, hashing de passwords con **bcrypt** y autenticacion stateless con **JWT**, todo manteniendo un estilo **funcional** (sin clases, DTOs como `dict`).

Este es el backend del ejemplo integrador; el frontend que lo consume vive en el repositorio `flask-auth-roles-example-web`.

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
flask-auth-roles-example-api/
├── app.py                          # Entry point Flask (puerto 5000)
├── docker-compose.yml              # MySQL 8 + volumen + script de inicializacion
├── requirements.txt                # Dependencias Python
├── .env.example                    # Template para configurar DB y JWT
├── flask_auth_roles_example/
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
├── db/
│   └── init_db.sql                 # Esquema (tabla usuarios)
└── docs/
    └── swagger.yaml                # Documentacion OpenAPI 3.0 de la API
```

## Documentacion (Swagger / OpenAPI)

La especificacion completa de la API en formato OpenAPI 3.0 vive en
[`docs/swagger.yaml`](docs/swagger.yaml). Incluye el esquema `BearerAuth` para los
endpoints protegidos por JWT. Se puede visualizar de varias formas:

- Pegando el contenido del archivo en [editor.swagger.io](https://editor.swagger.io).
- Abriendolo con la extension "Swagger Viewer" (o similar) en VSCode.
- Sirviendolo con cualquier renderer compatible con OpenAPI 3.

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

Una vez iniciada, la API estara disponible en `http://localhost:5000/flask_auth_roles_example_api`.

### 4. Crear el primer usuario admin

La tabla `usuarios` arranca vacia (no incluimos seed para evitar passwords hardcodeados). Para crear el primer admin, hace un `POST` al endpoint de registro indicando `rol: admin`:

```bash
curl -X POST http://localhost:5000/flask_auth_roles_example_api/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@admin.com","nombre":"Admin","password":"admin123","rol":"admin"}'
```

> En un sistema real, el campo `rol` **nunca** se aceptaria desde el body de `/register`. En este ejemplo lo dejamos abierto para simplificar el bootstrapping; en un caso real lo manejarias con un script de seed o un endpoint protegido por admin.

## Endpoints

Todos los endpoints estan bajo el prefijo `/flask_auth_roles_example_api`. Las respuestas son JSON; los errores siguen el formato:

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
curl -X POST http://localhost:5000/flask_auth_roles_example_api/register \
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
curl -X POST http://localhost:5000/flask_auth_roles_example_api/login \
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
curl http://localhost:5000/flask_auth_roles_example_api/me \
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
curl http://localhost:5000/flask_auth_roles_example_api/usuarios \
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

Ver `flask_auth_roles_example/db.py` para todos los ejemplos.

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

## Glosario de terminos

- **API REST**: estilo de arquitectura para servicios web que expone recursos via HTTP (GET, POST, PUT, DELETE) usando, en general, JSON como formato de intercambio.
- **Endpoint**: ruta concreta de la API (por ejemplo `POST /login`) que responde a un metodo HTTP y realiza una accion sobre un recurso.
- **Request / Response**: par de mensajes HTTP. La **request** es lo que envia el cliente (metodo, headers, body); la **response** es lo que devuelve el servidor (status code, headers, body).
- **Status code**: codigo numerico de la respuesta HTTP. Por ejemplo: `200 OK`, `201 Created`, `204 No Content`, `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `409 Conflict`.
- **Bearer token**: esquema de autenticacion HTTP donde el JWT viaja en el header `Authorization: Bearer <token>`.
- **Body**: contenido (payload) de una request o response. En esta API es JSON.
- **JSON**: formato de texto para representar datos estructurados (objetos y arrays). Es el formato usado para los bodies de request y response.
- **Flask**: micro framework web de Python. En este ejemplo se usa tanto en el frontend (renderizado server-side) como en la API backend.
- **Frontend**: aplicacion que renderiza las paginas HTML del lado del servidor y consume la API. En este ejemplo integrador corre en el puerto 5001 (`flask-auth-roles-example-web`).
- **Backend / API**: servicio HTTP REST (este proyecto) que expone los endpoints de autenticacion y usuarios. Corre en el puerto 5000.
- **Blueprint (Flask)**: mecanismo de Flask para agrupar rutas relacionadas en modulos (por ejemplo `routes/auth.py`, `routes/usuarios.py`).
- **Decorador (`@requiere_auth`)**: funcion de Python que envuelve a otra para agregarle comportamiento. Aca se usa para exigir un token valido (y opcionalmente un rol) antes de ejecutar la vista.
- **Autenticacion**: proceso de verificar **quien** es el usuario (login con email y password).
- **Autorizacion**: proceso de verificar **que** puede hacer el usuario autenticado (por ejemplo, si su rol es `admin`).
- **Rol**: etiqueta asociada al usuario que define sus permisos. En este proyecto: `admin` y `usuario`.
- **JWT (JSON Web Token)**: token firmado que contiene informacion del usuario (`sub`, `rol`, `exp`). La API lo emite en el login y el cliente lo envia en cada request protegida.
- **Claim**: cada uno de los campos dentro del payload de un JWT (`sub` = subject/id del usuario, `exp` = expiracion, etc.).
- **Stateless**: la API **no** guarda sesiones en memoria ni en base; cada request se autentica de cero validando el JWT.
- **`JWT_SECRET`**: clave secreta con la que se firman y verifican los tokens. Si se filtra, cualquiera puede emitir tokens validos.
- **Hashing**: transformacion **unidireccional** de un valor (por ejemplo una password) en una cadena de longitud fija. No se puede revertir.
- **bcrypt**: algoritmo de hashing pensado para passwords. Incluye un **salt** aleatorio y un factor de costo configurable.
- **Salt**: valor aleatorio que se mezcla con la password antes de hashearla para que dos passwords iguales generen hashes distintos.
- **Bootstrapping**: pasos iniciales para dejar el sistema usable (en este caso, crear el primer usuario `admin`).
- **Seed**: datos iniciales precargados en la base. En este proyecto **no** se hace seed para evitar passwords hardcodeadas.
- **SQLAlchemy**: libreria de Python para hablar con bases SQL. Aca se usa **sin ORM**, ejecutando SQL literal con `text()`.
- **ORM (Object Relational Mapper)**: capa que mapea tablas a clases/objetos. Este proyecto **no** lo usa para mantener el SQL explicito.
- **Query parametrizada**: query SQL en la que los valores se pasan como parametros (`:email`) y no concatenados al string, evitando **SQL injection**.
- **SQL injection**: vulnerabilidad por la que un atacante inyecta SQL malicioso a traves de inputs no sanitizados.
- **Migracion / esquema**: definicion de la estructura de la base (tablas, columnas). Aca vive en `db/init_db.sql`.
- **Docker / Docker Compose**: herramientas para correr servicios (en este caso MySQL) en contenedores aislados, definidos en `docker-compose.yml`.
- **Contenedor**: instancia en ejecucion de una imagen Docker (por ejemplo el contenedor de MySQL).
- **Volumen (Docker)**: almacenamiento persistente del contenedor; permite hacer `down` sin perder los datos.
- **`.env` / variables de entorno**: archivo con configuracion sensible (credenciales, secretos) que **no** se commitea al repo. `.env.example` es la plantilla.
- **Entorno virtual**: directorio aislado con la version de Python y las dependencias del proyecto, para no mezclarlas con las del sistema.
- **virtualenv / `venv`**: herramienta estandar de Python para crear entornos virtuales. Las dependencias se declaran en `requirements.txt` y se instalan con `pip install -r requirements.txt`. En este proyecto lo levantan los scripts `setup_virtualenv.sh` / `setup_virtualenv.bat`.
- **pipenv**: herramienta alternativa que combina la gestion del entorno virtual con la de dependencias en un solo flujo. Usa `Pipfile` (declaracion) y `Pipfile.lock` (versiones exactas resueltas) en vez de `requirements.txt`. En este proyecto lo levantan los scripts `setup_pipenv.sh` / `setup_pipenv.bat`.
- **`pip`**: gestor de paquetes de Python. Instala librerias desde PyPI dentro del entorno activo.
- **CORS (Cross-Origin Resource Sharing)**: mecanismo del navegador que controla que dominios pueden consumir la API. Relevante cuando el frontend corre en otro origen.
- **Validator**: funcion que verifica que el body de la request cumple las reglas (campos requeridos, formato, longitudes). Viven en `validators/`.
- **Service**: capa con la **logica de negocio** (registro, login, listar usuarios). Vive en `services/` y es invocada desde las routes.
- **DTO (Data Transfer Object)**: estructura usada para pasar datos entre capas. En este proyecto se modelan como `dict` de Python (estilo funcional, sin clases).

