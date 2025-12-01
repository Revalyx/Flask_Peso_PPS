# models.py
import re
from .db import get_connection
from werkzeug.security import generate_password_hash, check_password_hash


def validar_password(password: str) -> bool:
    """
    Política mínima ASVS Nivel 2:
    - Al menos 8 caracteres
    - Debe incluir letras y números
    """
    if len(password) < 8:
        return False

    if not re.search(r"[A-Za-z]", password):
        return False

    if not re.search(r"[0-9]", password):
        return False

    return True


class Usuario:

    @staticmethod
    def registrar(email, password, altura):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO users (email, password, altura)
            VALUES (?, ?, ?)
        """, (email, generate_password_hash(password), altura))

        conn.commit()
        user_id = cur.lastrowid
        conn.close()
        return user_id

    @staticmethod
    def login(email, password):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT id, password FROM users WHERE email=?", (email,))
        row = cur.fetchone()
        conn.close()

        if not row:
            return None

        user_id, hashed = row

        if check_password_hash(hashed, password):
            return user_id
        return None

    @staticmethod
    def get_altura(user_id):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT altura FROM users WHERE id=?", (user_id,))
        row = cur.fetchone()
        conn.close()

        return row[0] if row else None

    @staticmethod
    def actualizar_altura(user_id, altura):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET altura=? WHERE id=?", (altura, user_id))
        conn.commit()
        conn.close()


class RegistroPeso:

    @staticmethod
    def crear(user_id, peso, fecha):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO registros (user_id, peso, fecha)
            VALUES (?, ?, ?)
        """, (user_id, peso, fecha))

        conn.commit()
        conn.close()

    @staticmethod
    def obtener_por_usuario(user_id):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, peso, fecha
            FROM registros
            WHERE user_id=?
            ORDER BY fecha DESC
        """, (user_id,))

        rows = cur.fetchall()
        conn.close()

        return rows
