# src/models.py
from .db import get_connection
from datetime import datetime, timedelta  
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario:

    @staticmethod

    def registrar(email, password, altura, rol="usuario"):
        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute("""
                INSERT INTO users (email, password, altura, rol)
                VALUES (?, ?, ?, ?)
            """, (email, generate_password_hash(password), altura, rol))

            conn.commit()
            user_id = cur.lastrowid
            return user_id
        except Exception as e:
            print(f"Error en DB al registrar: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def login(email, password):
        conn = get_connection()
        cur = conn.cursor()
        
        # Pedimos el ROL a la base de datos
        cur.execute("SELECT id, password, intentos_fallidos, bloqueado_hasta, rol FROM users WHERE email=?", (email,))
        row = cur.fetchone()

        if not row:
            conn.close()
            return "NO_USER"

        user_id, password_hash, intentos, bloqueado_hasta, rol_db = row 
        
        # --- Lógica de bloqueo ---
        if bloqueado_hasta:
            bloqueo = datetime.strptime(bloqueado_hasta, "%Y-%m-%d %H:%M:%S")
            if datetime.now() < bloqueo:
                conn.close()
                return "BLOCKED"

        # --- Comprobar contraseña ---
        if check_password_hash(password_hash, password):
            cur.execute("UPDATE users SET intentos_fallidos=0, bloqueado_hasta=NULL WHERE id=?", (user_id,))
            conn.commit()
            conn.close()
            # Devolvemos ID y ROL real de la BD
            return (user_id, rol_db)
        else:
            # --- Fallo de contraseña ---
            nuevos_intentos = intentos + 1
            nuevo_bloqueo = None
            estado = "WRONG_PASS"
            
            if nuevos_intentos >= 5:
                nuevo_bloqueo = (datetime.now() + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
                estado = "BLOCKED_NOW"
            
            cur.execute("UPDATE users SET intentos_fallidos=?, bloqueado_hasta=? WHERE id=?", 
                       (nuevos_intentos, nuevo_bloqueo, user_id))
            conn.commit()
            conn.close()
            
            return estado

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

    @staticmethod
    def obtener_todos():
        conn = get_connection()
        cur = conn.cursor()
        
        # Traemos el email del usuario juntando las tablas
        cur.execute("""
            SELECT r.id, u.email, r.peso, r.fecha
            FROM registros r
            JOIN users u ON r.user_id = u.id
            ORDER BY r.fecha DESC
        """)
        
        rows = cur.fetchall()
        conn.close()
        return rows