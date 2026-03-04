from pathlib import Path
import sqlite3

DB_PATH = Path("peso.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    # Asegúrate de que el CREATE TABLE incluya 'rol'
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            altura INTEGER,
            intentos_fallidos INTEGER DEFAULT 0,
            bloqueado_hasta TEXT,
            rol TEXT DEFAULT 'usuario'  -- <--- ESTA LÍNEA ES IMPRESCINDIBLE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            peso REAL,
            fecha TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()
