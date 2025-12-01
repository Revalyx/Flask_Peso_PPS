# tests/test_app.py

import os
from src.app import app
from src.db import init_db, DB_PATH, get_connection


#################################
# RESETEAR BD ANTES DE CADA TEST
#################################

def setup_function():
    if DB_PATH.exists():
        os.remove(DB_PATH)
    init_db()


#################################
# HELPERS
#################################

TEST_EMAIL = "test@test.com"
TEST_PASS = "Testpass123"   # cumple política ASVS
TEST_ALTURA = "180"


def register_test_user(client):
    """Registrar usuario con altura obligatoria"""
    return client.post("/register", data={
        "email": TEST_EMAIL,
        "password": TEST_PASS,
        "altura": TEST_ALTURA
    }, follow_redirects=True)


def login_test_user(client):
    """Registrar + iniciar sesión"""
    register_test_user(client)
    return client.post("/login", data={
        "email": TEST_EMAIL,
        "password": TEST_PASS
    }, follow_redirects=True)


#################################
# TESTS
#################################

def test_home_requires_login():
    client = app.test_client()

    # SIN LOGIN → redirige a /login
    res = client.get("/")
    assert res.status_code == 302
    assert "/login" in res.location


def test_home_with_login():
    client = app.test_client()

    login_test_user(client)

    res = client.get("/")
    assert res.status_code == 200
    assert b"Panel" in res.data


def test_register_user():
    client = app.test_client()

    res = register_test_user(client)

    assert res.status_code == 200 or res.status_code == 302

    # Verificar que el usuario está realmente en la BD
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT email, altura FROM users WHERE email=?", (TEST_EMAIL,))
    row = cur.fetchone()
    conn.close()

    assert row is not None
    assert row[0] == TEST_EMAIL
    assert row[1] == int(TEST_ALTURA)


def test_register_peso_requires_login():
    client = app.test_client()

    res = client.post("/registro", data={
        "peso": "72",
        "fecha": "2025-11-21"
    })

    # SIN LOGIN → redirige
    assert res.status_code == 302
    assert "/login" in res.location


def test_register_peso_when_logged():
    client = app.test_client()

    login_test_user(client)

    res = client.post("/registro", data={
        "peso": "85",
        "fecha": "2025-11-22"
    }, follow_redirects=True)

    assert res.status_code == 200

    # Comprobar que se insertó en BD
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT peso, fecha FROM registros")
    row = cur.fetchone()
    conn.close()

    assert row is not None
    assert float(row[0]) == 85
    assert row[1] == "2025-11-22"


def test_historial_in_home():
    client = app.test_client()

    login_test_user(client)

    # Insertar un registro manual para probar visualización
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO registros (user_id, peso, fecha) VALUES (1, 90, '2025-11-23')")
    conn.commit()
    conn.close()

    res = client.get("/")

    assert res.status_code == 200
    assert b"90" in res.data
    assert b"2025-11-23" in res.data
