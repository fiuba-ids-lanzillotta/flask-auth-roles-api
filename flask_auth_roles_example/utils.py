import logging
import re
from datetime import datetime, timedelta, timezone
from functools import wraps

import bcrypt
import jwt
from flask import request, jsonify

from .constants import (
    JWT_SECRET,
    JWT_ALGORITHM,
    JWT_EXP_HORAS,
    ERROR_CODE_INVALID_MIN_VALUE,
    ERROR_CODE_INVALID_MAX_VALUE,
    ERROR_CODE_INVALID_EMAIL,
    ERROR_CODE_TOKEN_FALTANTE,
    ERROR_CODE_TOKEN_INVALIDO,
    ERROR_CODE_TOKEN_EXPIRADO,
    ERROR_CODE_SIN_PERMISO,
)

logger = logging.getLogger(__name__)

# Expresion regular simple para validar emails
REGEX_EMAIL = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


# ---------------------------------------------------------------
# Errores
# ---------------------------------------------------------------

def construir_error_api(code: str, message: str, description: str, level: str = 'error') -> dict:
    """Construye un payload de error compatible con el resto de la API."""
    return {
        'errors': [{
            'code': code,
            'message': message,
            'level': level,
            'description': description
        }]
    }


# ---------------------------------------------------------------
# Validaciones genericas
# ---------------------------------------------------------------

def validar_entero(numero, nombre: str = 'numero') -> int:
    try:
        return int(str(numero))
    except (ValueError, TypeError):
        logger.warning(f"Valor numerico invalido: '{numero}' no puede convertirse a entero")

        raise ValueError(construir_error_api(
            code=f'invalid.{nombre}.format',
            message=f"Formato de '{nombre}' invalido",
            description=f"El valor '{numero}' no puede convertirse a un numero entero"
        ))


def validar_minimo(valor: int, minimo: int, nombre: str) -> int:
    if valor < minimo:
        logger.warning(f"Valor por debajo del minimo: '{nombre}' es {valor}, minimo esperado {minimo}")

        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_MIN_VALUE,
            message='Valor por debajo del minimo permitido',
            description=f"El parametro '{nombre}' debe ser mayor o igual a {minimo}. Se recibio: {valor}"
        ))

    return valor


def validar_maximo(valor: int, maximo: int, nombre: str) -> int:
    if valor > maximo:
        logger.warning(f"Valor por encima del maximo: '{nombre}' es {valor}, maximo esperado {maximo}")

        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_MAX_VALUE,
            message='Valor por encima del maximo permitido',
            description=f"El parametro '{nombre}' debe ser menor o igual a {maximo}. Se recibio: {valor}"
        ))

    return valor


def validar_string_no_vacio(valor, nombre: str) -> str:
    if valor is None or not str(valor).strip():
        raise ValueError(construir_error_api(
            code=f'required.{nombre}',
            message=f"Campo requerido: '{nombre}'",
            description=f"El campo '{nombre}' es obligatorio y no puede estar vacio"
        ))

    return str(valor).strip()


def validar_largo_string(valor: str, minimo: int, maximo: int, nombre: str) -> str:
    if len(valor) < minimo:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_MIN_VALUE,
            message=f"Longitud minima no alcanzada en '{nombre}'",
            description=f"El campo '{nombre}' debe tener al menos {minimo} caracteres"
        ))

    if len(valor) > maximo:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_MAX_VALUE,
            message=f"Longitud maxima superada en '{nombre}'",
            description=f"El campo '{nombre}' debe tener como maximo {maximo} caracteres"
        ))

    return valor


def validar_formato_email(email: str) -> str:
    if not REGEX_EMAIL.match(email):
        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_EMAIL,
            message="Formato de 'email' invalido",
            description=f"El valor '{email}' no es un email valido"
        ))

    return email.lower()


# ---------------------------------------------------------------
# Passwords
# ---------------------------------------------------------------

def hashear_password(password: str) -> str:
    """Genera un hash bcrypt del password en texto plano."""
    hash_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    return hash_bytes.decode('utf-8')


def verificar_password(password: str, password_hash: str) -> bool:
    """Compara un password en texto plano contra un hash bcrypt."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except (ValueError, TypeError):
        return False


# ---------------------------------------------------------------
# JWT
# ---------------------------------------------------------------

def generar_token(usuario_id: int, rol: str) -> str:
    """Genera un JWT firmado con el id y el rol del usuario."""
    ahora = datetime.now(timezone.utc)
    payload = {
        'sub': str(usuario_id),
        'rol': rol,
        'iat': ahora,
        'exp': ahora + timedelta(hours=JWT_EXP_HORAS),
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decodificar_token(token: str) -> dict:
    """Decodifica un JWT y retorna su payload, o lanza ValueError con un error API."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_TOKEN_EXPIRADO,
            message='Token expirado',
            description='El token de autenticacion expiro. Volve a iniciar sesion.'
        ), 401)
    except jwt.InvalidTokenError:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_TOKEN_INVALIDO,
            message='Token invalido',
            description='El token de autenticacion no es valido.'
        ), 401)


def extraer_token_del_header() -> str:
    """Extrae el token JWT del header Authorization: Bearer <token>."""
    header = request.headers.get('Authorization', '')

    if not header.startswith('Bearer '):
        raise ValueError(construir_error_api(
            code=ERROR_CODE_TOKEN_FALTANTE,
            message='Token de autenticacion faltante',
            description='Debe enviarse el header Authorization con el formato "Bearer <token>"'
        ), 401)

    return header[len('Bearer '):].strip()


# ---------------------------------------------------------------
# Decorador de autenticacion
# ---------------------------------------------------------------

def requiere_auth(rol: str = None):
    """
    Decorador que valida el JWT del header Authorization y, opcionalmente,
    exige un rol especifico. Inyecta el payload en request.usuario_actual.
    """
    def decorador(funcion):
        @wraps(funcion)
        def wrapper(*args, **kwargs):
            try:
                token   = extraer_token_del_header()
                payload = decodificar_token(token)
            except ValueError as e:
                return jsonify(e.args[0]), e.args[1] if len(e.args) > 1 else 401

            if rol is not None and payload.get('rol') != rol:
                return jsonify(construir_error_api(
                    code=ERROR_CODE_SIN_PERMISO,
                    message='Permisos insuficientes',
                    description=f"Esta accion requiere el rol '{rol}'"
                )), 403

            request.usuario_actual = payload

            return funcion(*args, **kwargs)

        return wrapper

    return decorador
