from ..constants import ERROR_CODE_USUARIO_NOT_FOUND
from ..utils import construir_error_api
from .. import db


def construir_usuario_dto(usuario: dict) -> dict:
    """DTO publico de un usuario (sin password_hash)."""
    return {
        'id':     usuario['id'],
        'email':  usuario['email'],
        'nombre': usuario['nombre'],
        'rol':    usuario['rol'],
    }


def listar_usuarios() -> list[dict]:
    """Retorna todos los usuarios."""
    return [construir_usuario_dto(u) for u in db.obtener_todos_los_usuarios()]


def buscar_usuario_por_id(usuario_id: int) -> dict:
    """Busca un usuario por id. Retorna {} si no existe."""
    usuario = db.obtener_usuario_por_id(usuario_id)

    if not usuario:
        return {}

    return construir_usuario_dto(usuario)


def eliminar_usuario_por_id(usuario_id: int) -> None:
    """Elimina un usuario por id, o lanza ValueError si no existe."""
    if not db.obtener_usuario_por_id(usuario_id):
        raise ValueError(construir_error_api(
            code=ERROR_CODE_USUARIO_NOT_FOUND,
            message='Usuario no encontrado',
            description=f"No existe un usuario con id '{usuario_id}'"
        ), 404)

    db.eliminar_usuario(usuario_id)
