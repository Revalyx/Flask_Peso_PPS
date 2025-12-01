import os
from src.app import app
from src.db import init_db, DB_PATH, get_connection
from src.models import Usuario

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
    return client.post("/register", data={
        "email": "test@test.com",
        "password": "1234",
        "altura": "180"
    }, follow_redirects=True)


def login_test_user(client):
    register_test_user(client)
    return client.post("/login", data={
        "email": "test@test.com",
        "password": "1234"
    }, follow_redirects=True)


#################################
# TESTS DE RUTAS GET
#################################

def test_get_login_page():
    client = app.test_client()
    res = client.get("/login")
    assert res.status_code == 200
    assert b"Bienvenido" in res.data


def test_get_register_page():
    client = app.test_client()
    res = client.get("/register")
    assert res.status_code == 200
    assert b"Nueva Cuenta" in res.data


def test_logout_redirect():
    client = app.test_client()
    login_test_user(client)
    res = client.get("/logout", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.location


#################################
# TEST HOME
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
    assert b"Peso" in res.data


#################################
# TEST LOGIN
#################################

def test_login_valid():
    client = app.test_client()
    register_test_user(client)
    res = client.post("/login", data={
        "email": "test@test.com",
        "password": "1234"
    })
    assert res.status_code == 302
    assert res.location.endswith("/")


def test_login_invalid_credentials():
    client = app.test_client()
    res = client.post("/login", data={
        "email": "no@existe.com",
        "password": "wrong"
    })
    assert res.status_code == 200
    assert b"Credenciales incorrectas" in res.data


#################################
# TEST REGISTER
#################################

def test_register_user():
    client = app.test_client()
    res = register_test_user(client)
    assert res.status_code in (200, 302)

    conn = get_connection()
    row = conn.execute("SELECT email FROM users WHERE email=?", ("test@test.com",)).fetchone()
    conn.close()

    assert row is not None


def test_register_duplicate_user():
    client = app.test_client()

    register_test_user(client)

    res = client.post("/register", data={
        "email": "test@test.com",
        "password": "1234",
        "altura": "180"
    })

    assert res.status_code == 200
    assert b"El usuario ya existe" in res.data


#################################
# TEST REGISTRO PESO
#################################

def test_register_peso_requires_login():
    client = app.test_client()
    res = client.post("/registro", data={"peso": "70", "fecha": "2025-01-01"})
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
    row = conn.execute("SELECT peso, fecha FROM registros").fetchone()
    conn.close()

    assert row is not None
    assert float(row[0]) == 85
    assert row[1] == "2025-11-22"


#################################
# TEST HISTORIAL
#################################

def test_historial_in_home():
    client = app.test_client()
    login_test_user(client)

    conn = get_connection()
    conn.execute("INSERT INTO registros (user_id, peso, fecha) VALUES (1, 90, '2025-11-23')")
    conn.commit()
    conn.close()

    res = client.get("/")
    assert res.status_code == 200
    assert b"90" in res.data
    assert b"2025-11-23" in res.data


#################################
# TEST UPDATE HEIGHT
#################################

def test_update_height_redirects_if_not_logged():
    client = app.test_client()
    res = client.post("/update_height", data={"altura": "190"})
    assert res.status_code == 302
    assert "/login" in res.location


def test_update_height_success():
    client = app.test_client()
    login_test_user(client)

    res = client.post("/update_height", data={
        "altura": "190"
    }, follow_redirects=True)

    assert res.status_code == 200

    conn = get_connection()
    nueva_altura = conn.execute("SELECT altura FROM users WHERE id=1").fetchone()[0]
    conn.close()

    assert float(nueva_altura) == 190
