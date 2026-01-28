import os
from datetime import datetime, date

from src.app import app
from src.db import init_db, DB_PATH, get_connection
from src.models import Usuario, RegistroPeso


#################################
# RESETEAR BD ANTES DE CADA TEST
#################################

def setup_function():
    # ACTIVAMOS EL MODO TESTING PARA SALTAR EL CAPTCHA
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
        # En modo TESTING, el captcha da igual, pero el campo debe existir aunque sea vacío
        "g-recaptcha-response": "DUMMY_TOKEN" 
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
    # Como hay redirects por los flash messages, el status final suele ser 200
    assert res.status_code == 200

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
        "peso": "80",
        "fecha": "2023-11-21"
    })

    assert res.status_code == 302
    assert "/login" in res.location


def test_register_peso_when_logged():
    client = app.test_client()

    login_test_user(client)

    # USAMOS UNA FECHA PASADA PARA QUE NO FALLE LA VALIDACIÓN DE "NO FUTURO"
    fecha_pasada = "2023-01-01"

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
        "g-recaptcha-response": "dummy" # Enviamos algo para que no pete el request.form.get
    }, follow_redirects=True)

    assert res.status_code == 200


def test_register_peso_missing_data():
    client = app.test_client()
    login_test_user(client)

    res = client.post("/registro", data={}, follow_redirects=True)
    assert res.status_code == 200