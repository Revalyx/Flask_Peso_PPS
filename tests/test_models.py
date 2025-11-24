from src.models import Usuario, RegistroPeso
from src.db import get_connection, init_db, DB_PATH
import os

def setup_function():
    if DB_PATH.exists():
        os.remove(DB_PATH)
    init_db()

def test_insert_user():
    user_id = Usuario.registrar("a@a.com", "1234", 180)
    assert user_id == 1

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT email, altura FROM users WHERE id=1")
    row = cur.fetchone()
    conn.close()

    assert row[0] == "a@a.com"
    assert row[1] == 180

def test_insert_registro():
    user_id = Usuario.registrar("a@a.com", "1234", 180)
    RegistroPeso.crear(user_id, 70, "2025-11-20")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT peso, fecha FROM registros WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()

    assert row[0] == 70
    assert row[1] == "2025-11-20"
