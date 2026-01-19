from flask import Flask, request, session, redirect, render_template, flash
from datetime import datetime, date
import re

from .db import init_db, get_connection
from .models import Usuario, RegistroPeso





app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)


app.secret_key = "super_secret_key"



init_db()

EMAIL_REGEX = r"^[^@]+@[^@]+\.[^@]+$"

# ---------------- LOGIN ----------------
@app.get("/login")
def login():
    return render_template("login.html")

@app.post("/login")
def login_post():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    # ... (validaciones de campos vacíos igual) ...

    resultado = Usuario.login(email, password)

    if resultado == "NO_USER":
        flash("Credenciales incorrectas", "error")
    elif resultado == "BLOCKED":
        flash("Cuenta bloqueada temporalmente. Espera unos minutos.", "error")
    elif resultado == "BLOCKED_NOW":
        flash("Has fallado 3 veces. Tu cuenta ha sido bloqueada por 5 minutos.", "error")
    elif resultado == "WRONG_PASS":
        flash("Contraseña incorrecta", "error")
    else:
        # Es un ID numérico, pa' dentro
        session["user_id"] = resultado
        return redirect("/")
    
    return redirect("/login")

# ---------------- HOME ----------------
@app.get("/")
def home():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    registros = RegistroPeso.obtener_por_usuario(user_id)

    # Ordenar por fecha (como string YYYY-MM-DD funciona bien)
    registros = sorted(registros, key=lambda r: r[2])

    altura = Usuario.get_altura(user_id)

    ultimo_peso = registros[-1][1] if registros else 0

    imc = None
    estado = "—"
    color_estado = "#94a3b8"

    if altura and ultimo_peso:
        imc = round(ultimo_peso / ((altura / 100) ** 2), 2)

        if imc < 18.5:
            estado = "Bajo peso"
            color_estado = "#fbbf24"
        elif imc < 25:
            estado = "Normopeso"
            color_estado = "#4ade80"
        elif imc < 30:
            estado = "Sobrepeso"
            color_estado = "#fb923c"
        else:
            estado = "Obesidad"
            color_estado = "#ef4444"

    # 🔹 AQUÍ está el arreglo clave
    labels = [
        datetime.strptime(r[2], "%Y-%m-%d").strftime("%d/%m/%Y")
        for r in registros
    ]
    data = [r[1] for r in registros]

    return render_template(
        "home.html",
        registros=registros,
        peso_actual=ultimo_peso,
        imc=imc,
        estado=estado,
        color_estado=color_estado,
        altura=altura,
        labels=labels,
        data=data
    )
# ---------------- REGISTRO PESO ----------------
@app.post("/registro")
def registrar_peso():
    if "user_id" not in session:
        return redirect("/login")

    try:
        peso = float(request.form.get("peso"))
        if peso < 50 or peso > 300:
            raise ValueError
    except:
        flash("El peso debe estar entre 50 kg y 300 kg", "error")
        return redirect("/")


    try:
        fecha = datetime.strptime(request.form.get("fecha"), "%Y-%m-%d").date()
        if fecha > date.today():
            raise ValueError
    except:
        flash("No puedes registrar fechas futuras", "error")
        return redirect("/")

    RegistroPeso.crear(session["user_id"], peso, fecha)
    flash("Peso guardado correctamente", "success")
    return redirect("/")

# ---------------- REGISTER ----------------
@app.get("/register")
def register():
    return render_template("register.html")

@app.post("/register")
def register_post():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    altura_raw = request.form.get("altura", "")

    if not email or not password or not altura_raw:
        flash("Todos los campos son obligatorios", "error")
        return redirect("/register")

    if not re.match(EMAIL_REGEX, email):
        flash("Correo electrónico no válido", "error")
        return redirect("/register")

    if len(password) < 8:
        flash("La contraseña debe tener al menos 8 caracteres", "error")
        return redirect("/register")

    try:
        altura = float(altura_raw)
        if altura < 50 or altura > 300:
            raise ValueError
    except:
        flash("Altura no válida", "error")
        return redirect("/register")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email=?", (email,))
    if cur.fetchone():
        conn.close()
        flash("Ese email ya está registrado", "error")
        return redirect("/register")
    conn.close()

    Usuario.registrar(email, password, altura)
    flash("Cuenta creada correctamente", "success")
    return redirect("/login")

# ---------------- LOGOUT ----------------
@app.get("/logout")
def logout():
    session.clear()
    return redirect("/login")
