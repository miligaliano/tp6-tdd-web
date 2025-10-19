import sqlite3
import os

DB_FILE = "parque_aventura.db"


def obtener_conexion():
    """Crea y devuelve una conexión a la base de datos."""
    return sqlite3.connect(DB_FILE)


def crear_tabla_usuarios():
    """Crea la tabla de usuarios con campo para contraseña hasheada."""
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                email TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)
        conn.commit()


def buscar_usuario_por_email(email):
    """Busca un usuario por su email y devuelve sus datos si existe."""
    with obtener_conexion() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT email, nombre, password_hash FROM usuarios WHERE email = ?", (email,))
        return cursor.fetchone()
