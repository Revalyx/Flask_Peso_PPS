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

def register_test_user(client):
    """Registrar usuario con altura obligatoria"""
    return client.post("/register", data={
        "email": "test@test.com",
        "password": "1234",
        "altura": "180"
    }, follow_redirects=True)


def login_test_user(client):
    """Registrar + iniciar sesión"""
    register_test_user(client)
    return client.post("/login", data={
        "email": "test@test.com",
        "password": "1234"
    }, follow_redirects=True)


#################################
# TESTS
#################################

def test_home_requires_login():
    client = app.test_client()

    res = client.get("/")
    assert res.status_code == 302
    assert "/login" in res.location


def test_home_with_login():
    client = app.test_client()

    login_test_user(client)

    res = client.get("/")
    assert res.status_code == 200

    # FIX: Buscar un texto real en tu dashboard actual
    assert b"Peso" in res.data


def test_register_user():
    client = app.test_client()

    res = register_test_user(client)

    assert res.status_code == 200 or res.status_code == 302

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT email, altura FROM users WHERE email=?", ("test@test.com",))
    row = cur.fetchone()
    conn.close()

    assert row is not None
    assert row[0] == "test@test.com"
    assert row[1] == 180


def test_register_peso_requires_login():
    client = app.test_client()

    res = client.post("/registro", data={
        "peso": "72",
        "fecha": "2025-11-21"
    })

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

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO registros (user_id, peso, fecha) VALUES (1, 90, '2025-11-23')")
    conn.commit()
    conn.close()

    res = client.get("/")

    assert res.status_code == 200
    assert b"90" in res.data
    assert b"2025-11-23" in res.data
