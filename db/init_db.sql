-- =============================================================
--  Flask Auth Roles - Script DDL para MySQL
-- =============================================================
--  docker-compose lo ejecuta automaticamente al levantar el contenedor
--  (volumen montado en /docker-entrypoint-initdb.d).
--
--  La base `auth_roles` la crea el propio contenedor via MYSQL_DATABASE.
-- =============================================================

CREATE TABLE IF NOT EXISTS usuarios (
    id            INT          AUTO_INCREMENT PRIMARY KEY,
    email         VARCHAR(100) NOT NULL UNIQUE,
    nombre        VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol           ENUM('admin', 'usuario') NOT NULL DEFAULT 'usuario'
);

-- =============================================================
--  Para crear el primer usuario admin, hace un POST al endpoint
--  de registro indicando el rol "admin":
--
--    POST /flask_auth_roles_example_api/register
--    {
--      "email":    "admin@admin.com",
--      "nombre":   "Admin",
--      "password": "admin123",
--      "rol":      "admin"
--    }
-- =============================================================
