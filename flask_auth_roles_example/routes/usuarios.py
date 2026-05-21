from flask import Blueprint, jsonify, request

from ..constants import ROL_ADMIN, ERROR_CODE_USUARIO_NOT_FOUND
from ..utils import construir_error_api, requiere_auth, validar_entero, validar_minimo
from ..services.usuarios import (
    listar_usuarios,
    buscar_usuario_por_id,
    eliminar_usuario_por_id,
)

usuarios_bp = Blueprint('usuarios', __name__)


@usuarios_bp.route('/me', methods=['GET'])
@requiere_auth()
def get_me():
    """Retorna el usuario autenticado a partir del token."""
    payload    = request.usuario_actual
    usuario_id = int(payload['sub'])
    usuario    = buscar_usuario_por_id(usuario_id)

    if not usuario:
        return jsonify(construir_error_api(
            code=ERROR_CODE_USUARIO_NOT_FOUND,
            message='Usuario no encontrado',
            description=f"No existe un usuario con id '{usuario_id}'"
        )), 404

    return jsonify(usuario)


@usuarios_bp.route('/usuarios', methods=['GET'])
@requiere_auth(rol=ROL_ADMIN)
def get_usuarios():
    """Lista todos los usuarios. Solo accesible por administradores."""
    usuarios = listar_usuarios()

    if not usuarios:
        return '', 204

    return jsonify(usuarios)


@usuarios_bp.route('/usuarios/<usuario_id>', methods=['GET'])
@requiere_auth(rol=ROL_ADMIN)
def get_usuario(usuario_id):
    try:
        id_validado = validar_minimo(validar_entero(usuario_id, 'id'), 1, 'id')
    except ValueError as e:
        return jsonify(e.args[0]), 400

    usuario = buscar_usuario_por_id(id_validado)

    if not usuario:
        return jsonify(construir_error_api(
            code=ERROR_CODE_USUARIO_NOT_FOUND,
            message='Usuario no encontrado',
            description=f"No existe un usuario con id '{id_validado}'"
        )), 404

    return jsonify(usuario)


@usuarios_bp.route('/usuarios/<usuario_id>', methods=['DELETE'])
@requiere_auth(rol=ROL_ADMIN)
def delete_usuario(usuario_id):
    try:
        id_validado = validar_minimo(validar_entero(usuario_id, 'id'), 1, 'id')
    except ValueError as e:
        return jsonify(e.args[0]), 400

    try:
        eliminar_usuario_por_id(id_validado)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400

        return jsonify(e.args[0]), status

    return '', 204
