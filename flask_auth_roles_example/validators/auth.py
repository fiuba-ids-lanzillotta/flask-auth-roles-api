from ..constants import (
    PASSWORD_MIN_LEN,
    PASSWORD_MAX_LEN,
    ROL_USUARIO,
    ROLES_VALIDOS,
    ERROR_CODE_INVALID_BODY,
    ERROR_CODE_INVALID_ROL,
)
from ..utils import (
    construir_error_api,
    validar_string_no_vacio,
    validar_largo_string,
    validar_formato_email,
)


def _validar_body_presente(body):
    if body is None:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Cuerpo de la solicitud invalido',
            description='El cuerpo debe ser un JSON valido con Content-Type application/json'
        ))


def validar_body_login(body: dict) -> dict:
    """Valida el body del POST /login: email y password."""
    _validar_body_presente(body)

    errores = []
    email   = None
    password = None

    try:
        email = validar_string_no_vacio(body.get('email'), 'email')
        email = validar_formato_email(email)
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        password = validar_string_no_vacio(body.get('password'), 'password')
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    if errores:
        raise ValueError({'errors': errores})

    return {'email': email, 'password': password}


def validar_body_registro(body: dict) -> dict:
    """Valida el body del POST /register: email, nombre, password y rol opcional."""
    _validar_body_presente(body)

    errores  = []
    email    = None
    nombre   = None
    password = None
    rol      = None

    try:
        email = validar_string_no_vacio(body.get('email'), 'email')
        email = validar_formato_email(email)
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        nombre = validar_string_no_vacio(body.get('nombre'), 'nombre')
        nombre = validar_largo_string(nombre, 1, 100, 'nombre')
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        password = validar_string_no_vacio(body.get('password'), 'password')
        password = validar_largo_string(password, PASSWORD_MIN_LEN, PASSWORD_MAX_LEN, 'password')
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    rol_raw = body.get('rol')

    if rol_raw is None:
        rol = ROL_USUARIO
    else:
        try:
            rol = validar_string_no_vacio(rol_raw, 'rol').lower()
            
            if rol not in ROLES_VALIDOS:
                raise ValueError(construir_error_api(
                    code=ERROR_CODE_INVALID_ROL,
                    message="Rol invalido",
                    description=f"El rol '{rol}' no es valido. Valores permitidos: {', '.join(ROLES_VALIDOS)}"
                ))
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if errores:
        raise ValueError({'errors': errores})

    return {
        'email':    email,
        'nombre':   nombre,
        'password': password,
        'rol':      rol,
    }
