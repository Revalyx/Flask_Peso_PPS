from src.app import app
from src.db import init_db, DB_PATH
import os

def setup_function():
    # Resetear BD antes de cada test
    if DB_PATH.exists():
        os.remove(DB_PATH)
    init_db()

def register_test_user(client):
    """Crea un usuario de pruebas con email + contraseña."""
    return client.post("/register", data={
        "email": "test@test.com",
        "password": "1234"
    })

def login_test_user(client):
    """Inicia sesión con usuario de pruebas."""
    register_test_user(client)
    return client.post("/login", data={
        "email": "test@test.com",
        "password": "1234"
    })

def test_home():
    client = app.test_client()

    # Sin login → redirige a /login
    res = client.get("/")
    assert res.status_code == 302

    # Con login → OK
    login_test_user(client)
    res = client.get("/")
    assert res.status_code == 200

def test_registro():
    client = app.test_client()

    # Sin login → redirige
    res = client.post("/registro", data={"peso": 80, "fecha": "2025-11-21"})
    assert res.status_code == 302

    # Con login → crear registro de peso
    login_test_user(client)
    res = client.post("/registro", data={"peso": 80, "fecha": "2025-11-21"})
    # Redirige a "/" después de registrar, por eso 302 es correcto
    assert res.status_code == 302
