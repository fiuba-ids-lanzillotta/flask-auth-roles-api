from sqlalchemy import create_engine, text
from .constants import DB_URL

# Motor de conexion compartido por toda la aplicacion.
# El pool de conexiones lo maneja SQLAlchemy automaticamente.
motor = create_engine(DB_URL, pool_pre_ping=True)


# ---------------------------------------------------------------
# Funciones de soporte
# ---------------------------------------------------------------

def fila_a_dict(fila) -> dict:
    """Convierte una fila del resultado de una query en un diccionario."""
    return dict(fila._mapping)


def ejecutar_consulta(sql: str, parametros: dict = None) -> list[dict]:
    """Ejecuta una SELECT y devuelve todas las filas como lista de dicts."""
    with motor.connect() as conexion:
        resultado = conexion.execute(text(sql), parametros or {})

        return [fila_a_dict(fila) for fila in resultado]


def ejecutar_mutacion(sql: str, parametros: dict = None) -> int:
    """
    Ejecuta un INSERT, UPDATE o DELETE y hace commit.
    Retorna el id autoincremental generado por el INSERT (0 si no aplica).
    """
    with motor.begin() as conexion:
        resultado = conexion.execute(text(sql), parametros or {})

        return resultado.lastrowid or 0


# ---------------------------------------------------------------
# Queries de usuarios
# ---------------------------------------------------------------

def obtener_todos_los_usuarios() -> list[dict]:
    """Retorna todos los usuarios ordenados por id (sin el hash de password)."""
    sql = 'SELECT id, email, nombre, rol FROM usuarios ORDER BY id'

    return ejecutar_consulta(sql)


def obtener_usuario_por_id(usuario_id: int) -> dict:
    """Retorna el usuario con el id dado, o un dict vacio si no existe."""
    sql   = 'SELECT id, email, nombre, rol FROM usuarios WHERE id = :id'
    filas = ejecutar_consulta(sql, {'id': usuario_id})

    return filas[0] if filas else {}


def obtener_usuario_por_email(email: str) -> dict:
    """
    Retorna el usuario con el email dado incluyendo el password_hash,
    o un dict vacio si no existe. Se usa solo durante el login.
    """
    sql   = 'SELECT id, email, nombre, rol, password_hash FROM usuarios WHERE email = :email'
    filas = ejecutar_consulta(sql, {'email': email})

    return filas[0] if filas else {}


def insertar_usuario(email: str, nombre: str, password_hash: str, rol: str) -> int:
    """Inserta un nuevo usuario y retorna el id generado."""
    sql = """
        INSERT INTO usuarios (email, nombre, password_hash, rol)
        VALUES (:email, :nombre, :password_hash, :rol)
    """

    return ejecutar_mutacion(sql, {
        'email':         email,
        'nombre':        nombre,
        'password_hash': password_hash,
        'rol':           rol,
    })


def eliminar_usuario(usuario_id: int) -> int:
    """Elimina un usuario por id."""
    sql = 'DELETE FROM usuarios WHERE id = :id'

    return ejecutar_mutacion(sql, {'id': usuario_id})
