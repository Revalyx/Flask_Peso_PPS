# models.py
from .db import get_connection
from datetime import datetime, timedelta  
from werkzeug.security import generate_password_hash, check_password_hash


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
        # Pedimos los campos de seguridad extra
        cur.execute("SELECT id, password, intentos_fallidos, bloqueado_hasta FROM users WHERE email=?", (email,))
        row = cur.fetchone()

        if not row:
            conn.close()
            return "NO_USER"

        user_id, password_hash, intentos, bloqueado_hasta = row
        
        # --- PASO 1: VERIFICAR SI ESTÁ CASTIGADO ---
        if bloqueado_hasta:
            bloqueo = datetime.strptime(bloqueado_hasta, "%Y-%m-%d %H:%M:%S")
            if datetime.now() < bloqueo:
                conn.close()
                return "BLOCKED" # Aún le queda tiempo

        # --- PASO 2: COMPROBAR CONTRASEÑA ---
        if check_password_hash(password_hash, password):
            # ¡Entró! Borrón y cuenta nueva
            cur.execute("UPDATE users SET intentos_fallidos=0, bloqueado_hasta=NULL WHERE id=?", (user_id,))
            conn.commit()
            conn.close()
            return user_id
        else:
            # ¡Falló! Sumamos uno
            nuevos_intentos = intentos + 1
            nuevo_bloqueo = None
            estado = "WRONG_PASS"
            
            # CAMBIO AQUÍ: Usamos 5 intentos y 15 minutos (como dice tu MD)
            if nuevos_intentos >= 5:
                # 15 minutos de castigo
                nuevo_bloqueo = (datetime.now() + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
                estado = "BLOCKED_NOW"
            
            # Guardamos el desastre en la BD
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
