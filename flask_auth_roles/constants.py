import os
from dotenv import load_dotenv

load_dotenv()

# URL base de la API
BASE_URL = '/flask_auth_roles_api'

# Roles permitidos en el sistema
ROL_ADMIN   = 'admin'
ROL_USUARIO = 'usuario'
ROLES_VALIDOS = (ROL_ADMIN, ROL_USUARIO)

# Reglas de dominio sobre el password
PASSWORD_MIN_LEN = 6
PASSWORD_MAX_LEN = 64

# Configuracion JWT
JWT_SECRET     = os.getenv('JWT_SECRET', 'change-me-please')
JWT_ALGORITHM  = 'HS256'
JWT_EXP_HORAS  = int(os.getenv('JWT_EXP_HORAS', '8'))

# Configuracion de la base de datos MySQL (levantada via docker-compose)
DB_HOST     = os.getenv('DB_HOST', 'localhost')
DB_PORT     = int(os.getenv('DB_PORT', '3306'))
DB_USER     = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
DB_NAME     = os.getenv('DB_NAME', 'auth_roles')
DB_URL      = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Codigos de error
ERROR_CODE_INVALID_BODY        = 'invalid.body'
ERROR_CODE_INVALID_MIN_VALUE   = 'invalid.min.value'
ERROR_CODE_INVALID_MAX_VALUE   = 'invalid.max.value'
ERROR_CODE_INVALID_EMAIL       = 'invalid.email.format'
ERROR_CODE_INVALID_ROL         = 'invalid.rol'
ERROR_CODE_EMAIL_YA_REGISTRADO = 'email.already.registered'
ERROR_CODE_CREDENCIALES        = 'invalid.credentials'
ERROR_CODE_TOKEN_FALTANTE      = 'auth.token.missing'
ERROR_CODE_TOKEN_INVALIDO      = 'auth.token.invalid'
ERROR_CODE_TOKEN_EXPIRADO      = 'auth.token.expired'
ERROR_CODE_SIN_PERMISO         = 'auth.forbidden'
ERROR_CODE_USUARIO_NOT_FOUND   = 'usuario.not.found'
