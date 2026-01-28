import os
from datetime import datetime

from src.app import app
from src.db import init_db, DB_PATH, get_connection
from src.models import Usuario, RegistroPeso


#################################
# RESETEAR BD ANTES DE CADA TEST
#################################

def setup_function():
    # 🔥 ACTIVAMOS EL MODO TESTING (PASE VIP PARA EL CAPTCHA)
    app.config['TESTING'] = True
    
    if DB_PATH.exists():
        os.remove(DB_PATH)
    init_db()


#################################
# HELPERS
#################################

def register_test_user(client):
    return client.post("/register", data={
        "email": "test@test.com",
        "password": "PesoApp2025!", 
        "altura": "180",
        # Aunque tengamos pase VIP, enviamos un token falso por si acaso
        "g-recaptcha-response": "TOKEN_DE_PRUEBA" 
    }, follow_redirects=True)


def login_test_user(client):
    register_test_user(client)
    return client.post("/login", data={
        "email": "test@test.com",
        "password": "PesoApp2025!"
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
    assert b"Peso" in res.data or b"Panel" in res.data


def test_register_user():
    client = app.test_client()

    res = register_test_user(client)
    assert res.status_code in (200, 302)

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

    # Usamos fecha pasada para evitar conflictos
    res = client.post("/registro", data={
        "peso": "80",
        "fecha": "2023-11-21"
    })

    assert res.status_code == 302
    assert "/login" in res.location


def test_register_peso_when_logged():
    client = app.test_client()

    login_test_user(client)

    # 🔥 CAMBIO IMPORTANTE: Usamos una fecha pasada (2023) 
    # para que tu validación de "no fechas futuras" no falle el test.
    fecha_pasada = "2023-11-22"

    res = client.post("/registro", data={
        "peso": "85",
        "fecha": fecha_pasada
    }, follow_redirects=True)

    assert res.status_code == 200

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT peso, fecha FROM registros")
    row = cur.fetchone()
    conn.close()

    assert row is not None
    assert float(row[0]) == 85
    assert row[1] == fecha_pasada


def test_historial_in_home():
    client = app.test_client()

    login_test_user(client)

    # Insertamos un registro con fecha pasada
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO registros (user_id, peso, fecha) VALUES (1, 90, '2023-11-23')"
    )
    conn.commit()
    conn.close()

    res = client.get("/")

    assert res.status_code == 200
    assert b"90" in res.data

def test_get_login():
    client = app.test_client()
    res = client.get("/login")
    assert res.status_code == 200


def test_get_register():
    client = app.test_client()
    res = client.get("/register")
    assert res.status_code == 200


def test_login_wrong_credentials():
    client = app.test_client()
    register_test_user(client)

    res = client.post("/login", data={
        "email": "test@test.com",
        "password": "wrongpass"
    }, follow_redirects=True)

    assert res.status_code == 200


def test_register_duplicate_email():
    client = app.test_client()
    register_test_user(client)

    res = client.post("/register", data={
        "email": "test@test.com",
        "password": "12345678",
        "altura": "180",
        "g-recaptcha-response": "TOKEN_TEST"
    }, follow_redirects=True)

    assert res.status_code == 200


def test_register_peso_missing_data():
    client = app.test_client()
    login_test_user(client)

    res = client.post("/registro", data={}, follow_redirects=True)
    assert res.status_code == 200