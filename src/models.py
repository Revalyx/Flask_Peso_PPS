import hashlib
from .db import get_connection

class Usuario:
    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def registrar(email, password):
        conn = get_connection()
        cur = conn.cursor()

        hashed = Usuario.hash_password(password)

        cur.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed))
        conn.commit()
        uid = cur.lastrowid
        conn.close()
        return uid

    @staticmethod
    def login(email, password):
        conn = get_connection()
        cur = conn.cursor()

        hashed = Usuario.hash_password(password)
        cur.execute("SELECT id FROM users WHERE email = ? AND password = ?", (email, hashed))
        row = cur.fetchone()

        conn.close()
        return row[0] if row else None


class RegistroPeso:
    def __init__(self, peso, fecha):
        self.peso = peso
        self.fecha = fecha

    def to_dict(self):
        return {
            "peso": self.peso,
            "fecha": self.fecha
        }

    @staticmethod
    def crear(user_id, peso, fecha):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO registros (user_id, peso, fecha) VALUES (?, ?, ?)",
            (user_id, peso, fecha)
        )

        conn.commit()
        conn.close()
