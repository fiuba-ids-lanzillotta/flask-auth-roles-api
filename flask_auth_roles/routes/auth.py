from flask import Blueprint, jsonify, request

from ..services.auth import registrar_usuario, autenticar_usuario

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def post_register():
    body = request.get_json(silent=True)

    try:
        usuario = registrar_usuario(body)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400

        return jsonify(e.args[0]), status

    return jsonify(usuario), 201


@auth_bp.route('/login', methods=['POST'])
def post_login():
    body = request.get_json(silent=True)

    try:
        resultado = autenticar_usuario(body)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400

        return jsonify(e.args[0]), status

    return jsonify(resultado)
