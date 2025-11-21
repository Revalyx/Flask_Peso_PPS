from flask import Flask, request, session, redirect, render_template_string
from .db import init_db, get_connection
from .models import Usuario, RegistroPeso

app = Flask(__name__)
app.secret_key = "super_secret_key"

init_db()

# -------------------------- CSS SIMPLE --------------------------
PAGE_STYLE = """
<style>
    body { 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
        background: linear-gradient(135deg, #2f80ed, #56ccf2);
        margin: 0;
        height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
        color: #333;
    }

    .box {
        background: white;
        padding: 30px;
        border-radius: 14px;
        width: 380px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.15);
        animation: fadeIn 0.4s ease;
    }

    h2 {
        margin-bottom: 15px;
        text-align: center;
        font-weight: 700;
        color: #222;
    }

    input {
        width: 100%;
        padding: 12px;
        margin-top: 10px;
        border-radius: 8px;
        border: 1px solid #ccc;
        font-size: 15px;
        transition: 0.2s;
        background: #fafafa;
    }

    input:focus {
        outline: none;
        border-color: #2f80ed;
        background: #fff;
        box-shadow: 0 0 6px rgba(47,128,237,0.4);
    }

    button {
        width: 100%;
        padding: 12px;
        margin-top: 15px;
        border-radius: 8px;
        background: #2f80ed;
        color: white;
        border: none;
        cursor: pointer;
        font-size: 15px;
        font-weight: 600;
        transition: 0.2s;
    }

    button:hover {
        background: #1769d1;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }

    a {
        display: block; 
        margin-top: 15px; 
        text-align: center;
        color: #2f80ed;
        text-decoration: none;
        font-size: 14px;
        transition: 0.2s;
    }

    a:hover {
        color: #134f96;
        text-decoration: underline;
    }

    h3 {
        margin-top: 25px;
        font-weight: 600;
        color: #222;
        border-bottom: 2px solid #e5e5e5;
        padding-bottom: 5px;
    }

    .peso-item {
        background: #f1f8ff;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 8px;
        border: 1px solid #d6eaff;
        font-size: 14px;
        display: flex;
        justify-content: space-between;
        color: #134f96;
        font-weight: 500;
        transition: 0.2s;
    }

    .peso-item:hover {
        background: #e7f2ff;
        border-color: #b2d6ff;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(15px); }
        to   { opacity: 1; transform: translateY(0); }
    }
</style>
"""



# -------------------------- Login --------------------------
@app.get("/login")
def login():
    return render_template_string(PAGE_STYLE + """
    <div class="box">
        <h2>Iniciar sesión</h2>
        <form method="POST">
            <input name="email" placeholder="Email" required>
            <input type="password" name="password" placeholder="Contraseña" required>
            <button>Entrar</button>
        </form>
        <a href="/register">Crear cuenta</a>
    </div>
    """)

@app.post("/login")
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")

    user_id = Usuario.login(email, password)
    if not user_id:
        return render_template_string(PAGE_STYLE + """
        <div class="box">
            <h2>Error</h2>
            <p>Email o contraseña incorrectos.</p>
            <a href="/login">Volver</a>
        </div>
        """)

    session["user_id"] = user_id
    return redirect("/")

# -------------------------- Registro --------------------------
@app.get("/register")
def register():
    return render_template_string(PAGE_STYLE + """
    <div class="box">
        <h2>Crear cuenta</h2>
        <form method="POST">
            <input name="email" placeholder="Email" required>
            <input type="password" name="password" placeholder="Contraseña" required>
            <button>Registrar</button>
        </form>
        <a href="/login">Volver al login</a>
    </div>
    """)

@app.post("/register")
def register_post():
    email = request.form.get("email")
    password = request.form.get("password")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email=?", (email,))
    existe = cur.fetchone()
    conn.close()

    if existe:
        return render_template_string(PAGE_STYLE + """
        <div class="box">
            <h2>Error</h2>
            <p>Este email ya está registrado.</p>
            <a href="/register">Volver</a>
        </div>
        """)

    user_id = Usuario.registrar(email, password)
    session["user_id"] = user_id
    return redirect("/")

# -------------------------- Home --------------------------
@app.get("/")
def home():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT peso, fecha FROM registros WHERE user_id=?", (session["user_id"],))
    registros = cur.fetchall()
    conn.close()

    lista_html = "".join(
        f"<div class='peso-item'>📅 {r[1]} — {r[0]} kg</div>"
        for r in registros
    )

    return render_template_string(PAGE_STYLE + f"""
    <div class="box">
        <h2>Registrar peso</h2>

        <form method="POST" action="/registro">
            <input type="number" step="0.01" name="peso" placeholder="Peso (kg)" required>
            <input type="date" name="fecha" required>
            <button type="submit">Guardar</button>
        </form>

        <h3 style="margin-top:25px;">Historial</h3>
        {lista_html if lista_html else "<p>No hay registros aún.</p>"}

        <a href="/logout">Cerrar sesión</a>
    </div>
    """)

# -------------------------- Guardar peso --------------------------
@app.post("/registro")
def registrar_peso():
    if "user_id" not in session:
        return redirect("/login")

    peso = request.form.get("peso")
    fecha = request.form.get("fecha")

    RegistroPeso.crear(session["user_id"], peso, fecha)
    return redirect("/")

# -------------------------- Logout --------------------------
@app.get("/logout")
def logout():
    session.clear()
    return redirect("/login")
