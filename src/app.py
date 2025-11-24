# app.py
from flask import Flask, request, session, redirect, render_template
from .db import init_db
from .models import Usuario, RegistroPeso

app = Flask(__name__, template_folder="../templates")
app.secret_key = "super_secret_key"

init_db()


# LOGIN
@app.get("/login")
def login():
    return render_template("login.html")


@app.post("/login")
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")

    user_id = Usuario.login(email, password)
    if not user_id:
        return render_template("login.html", error="Email o contraseña incorrectos")

    session["user_id"] = user_id
    return redirect("/")


# REGISTER
@app.get("/register")
def register():
    return render_template("register.html")


@app.post("/register")
def register_post():
    email = request.form.get("email")
    password = request.form.get("password")
    altura = request.form.get("altura")

    if not altura:
        return render_template("register.html", error="La altura es obligatoria.")

    user_id = Usuario.registrar(email, password, altura)
    session["user_id"] = user_id
    return redirect("/")


# PANEL
@app.get("/")
def home():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    altura = Usuario.get_altura(user_id)
    registros_raw = RegistroPeso.obtener_por_usuario(user_id)

    historial = []
    if altura:
        altura_m = altura / 100
        for rid, peso, fecha in registros_raw:
            imc = float(peso) / (altura_m ** 2)
            historial.append({
                "id": rid,
                "peso": peso,
                "fecha": fecha,
                "imc": round(imc, 1)
            })

    return render_template("home.html", registros=historial)


# GUARDAR PESO
@app.post("/registro")
def registrar_peso():
    if "user_id" not in session:
        return redirect("/login")

    peso = request.form.get("peso")
    fecha = request.form.get("fecha")

    if peso and fecha:
        RegistroPeso.crear(session["user_id"], peso, fecha)

    return redirect("/")


# EDITAR ALTURA
@app.get("/edit-height")
def edit_height():
    if "user_id" not in session:
        return redirect("/login")

    return render_template("edit_altura.html")


@app.post("/edit-height")
def edit_height_post():
    if "user_id" not in session:
        return redirect("/login")

    altura = request.form.get("altura")
    Usuario.actualizar_altura(session["user_id"], altura)

    return redirect("/")


# LOGOUT
@app.get("/logout")
def logout():
    session.clear()
    return redirect("/login")
