from ..constants import (
    ERROR_CODE_CREDENCIALES,
    ERROR_CODE_EMAIL_YA_REGISTRADO,
)
from ..utils import (
    construir_error_api,
    hashear_password,
    verificar_password,
    generar_token,
)
from ..validators.auth import validar_body_login, validar_body_registro
from .. import db
from .usuarios import construir_usuario_dto


def registrar_usuario(body: dict) -> dict:
    """
    Valida el body, verifica que el email no este registrado e inserta el usuario.
    Retorna el DTO publico del usuario recien creado.
    """
    datos = validar_body_registro(body)

    if db.obtener_usuario_por_email(datos['email']):
        raise ValueError(construir_error_api(
            code=ERROR_CODE_EMAIL_YA_REGISTRADO,
            message='Email ya registrado',
            description=f"Ya existe un usuario con email '{datos['email']}'"
        ), 409)

    nuevo_id = db.insertar_usuario(
        email=datos['email'],
        nombre=datos['nombre'],
        password_hash=hashear_password(datos['password']),
        rol=datos['rol'],
    )

    return construir_usuario_dto({
        'id':     nuevo_id,
        'email':  datos['email'],
        'nombre': datos['nombre'],
        'rol':    datos['rol'],
    })


def autenticar_usuario(body: dict) -> dict:
    """
    Valida el body, verifica las credenciales y retorna el token y el DTO del usuario.
    """
    datos   = validar_body_login(body)
    usuario = db.obtener_usuario_por_email(datos['email'])

    if not usuario or not verificar_password(datos['password'], usuario['password_hash']):
        raise ValueError(construir_error_api(
            code=ERROR_CODE_CREDENCIALES,
            message='Credenciales invalidas',
            description='El email o password son incorrectos'
        ), 401)

    token = generar_token(usuario_id=usuario['id'], rol=usuario['rol'])

    return {
        'token':   token,
        'usuario': construir_usuario_dto(usuario),
    }
