from flask import Flask, request, session, redirect, render_template, flash, make_response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies
from flasgger import Swagger
from datetime import timedelta, datetime, date
from flask_jwt_extended import get_jwt
from .app_endpoints import api_bp
import re
from .db import init_db, get_connection
from .models import Usuario, RegistroPeso
import requests

COMMON_PASSWORDS = {
    "12345612", "password", "12345678", "qwerty", "12345", 
    "123456789", "football", "skywalker", "princess", "admin",
    "welcome", "1234567", "monkey", "dragon", "master"
}

# Configuración de la aplicación Flask

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)

# Configuración básica del panel Swagger
swagger_config = {
    "headers": [],
    "specs": [{"endpoint": 'apispec_1', "route": '/apispec_1.json'}],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/", 
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header. Ejemplo: 'Bearer <tu_token>'"
        }
    }
}
swagger = Swagger(app, config=swagger_config)

app.secret_key = "super_secret_key"

# Registramos las rutas de la API con el prefijo /api
app.register_blueprint(api_bp, url_prefix='/api')

app.config["JWT_SECRET_KEY"] = "super_secret_jwt_key"
app.config["JWT_TOKEN_LOCATION"] = ["cookies","headers"]
app.config["JWT_COOKIE_SECURE"] = False  
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1) 

jwt = JWTManager(app)

@jwt.unauthorized_loader
def missing_token_callback(error_string):
    flash("Acceso denegado. Por favor, inicia sesión.", "error")
    return redirect("/login")

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    flash("Tu sesión ha caducado. Inicia sesión de nuevo.", "error")
    return redirect("/login")

init_db()

EMAIL_REGEX = r"^[^@]+@[^@]+\.[^@]+$"
RECAPTCHA_SITE_KEY = "6LfpMFksAAAAAHl0R2BcAUyQv2DLGzC9_k-SivMH"
RECAPTCHA_SECRET_KEY = "6LfpMFksAAAAAN6tCj_olsGd7DqUIIQOconc2wYu"

CSP_POLICY = {
    'default-src': ["'self'"],
    'script-src': ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net", "https://www.google.com", "https://www.gstatic.com"],
    'style-src': ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net", "https://fonts.googleapis.com"],
    'font-src': ["'self'", "https://fonts.gstatic.com"],
    'frame-src': ["https://www.google.com"],
    'img-src': ["'self'", "data:"]
}

csp_string = "; ".join([f"{k} {' '.join(v)}" for k, v in CSP_POLICY.items()])

@app.after_request
def aplicar_seguridad(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = csp_string
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response

def validar_captcha(response_token):
    if app.config.get("TESTING"): return True
    if not response_token: return False
    payload = {'secret': RECAPTCHA_SECRET_KEY, 'response': response_token}
    try:
        r = requests.post("https://www.google.com/recaptcha/api/siteverify", data=payload)
        return r.json().get("success", False)
    except: return False

# ---------------- LOGIN ----------------
@app.get("/login")
def login():
    """
    Renderiza la página de login
    ---
    tags:
      - Autenticación
    responses:
      200:
        description: Página de login cargada
    """
    return render_template("login.html")

@app.post("/login")
def login_post():
    """
    Procesa las credenciales de login
    ---
    tags:
      - Autenticación
    parameters:
      - name: email
        in: formData
        type: string
        required: true
      - name: password
        in: formData
        type: string
        required: true
    responses:
      302:
        description: Redirección al Home
      401:
        description: Error en credenciales
    """
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    resultado = Usuario.login(email, password)
    if resultado == "NO_USER": flash("Credenciales incorrectas", "error")
    elif resultado == "BLOCKED": flash("Cuenta bloqueada temporalmente.", "error")
    elif resultado == "BLOCKED_NOW": flash("Has fallado muchas veces. Bloqueo de 15 min.", "error")
    elif resultado == "WRONG_PASS": flash("Contraseña incorrecta", "error")
    else:
        user_id, rol_real = resultado 
        additional_claims = {"rol": rol_real}
        access_token = create_access_token(identity=str(user_id), additional_claims=additional_claims)
        resp = redirect("/")
        set_access_cookies(resp, access_token)
        return resp
    return redirect("/login")

# ---------------- HOME ----------------
@app.get("/")
@jwt_required()
def home():
    """
    Vista principal del usuario
    ---
    tags:
      - Gestión de Peso
    security:
      - Bearer: []
    responses:
      200:
        description: Dashboard cargado exitosamente
      401:
        description: No autorizado
    """
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    es_admin = claims.get("rol") == "admin"
    registros = RegistroPeso.obtener_por_usuario(current_user_id)
    registros = sorted(registros, key=lambda r: r[2])
    altura = Usuario.get_altura(current_user_id)
    ultimo_peso = registros[-1][1] if registros else 0
    imc = None
    estado = "—"
    color_estado = "#94a3b8"
    if altura and ultimo_peso:
        imc = round(ultimo_peso / ((altura / 100) ** 2), 2)
        if imc < 18.5: estado, color_estado = "Bajo peso", "#fbbf24"
        elif imc < 25: estado, color_estado = "Normopeso", "#4ade80"
        elif imc < 30: estado, color_estado = "Sobrepeso", "#fb923c"
        else: estado, color_estado = "Obesidad", "#ef4444"
    labels = [datetime.strptime(r[2], "%Y-%m-%d").strftime("%d/%m/%Y") for r in registros]
    data = [r[1] for r in registros]
    return render_template("home.html", registros=registros, peso_actual=ultimo_peso, imc=imc, estado=estado, color_estado=color_estado, altura=altura, labels=labels, data=data, hoy=date.today().strftime("%Y-%m-%d"), es_admin=es_admin)

# ---------------- REGISTRO PESO ----------------
@app.post("/registro")
@jwt_required()
def registrar_peso():
    """
    Registrar nuevo registro de peso
    ---
    tags:
      - Gestión de Peso
    security:
      - Bearer: []
    parameters:
      - name: peso
        in: formData
        type: number
        required: true
      - name: fecha
        in: formData
        type: string
        required: true
    responses:
      302:
        description: Éxito
      400:
        description: Fallo en validación
    """
    claims = get_jwt()
    if claims.get("rol") == "admin":
        flash("El Administrador no puede registrar pesos, ¡solo vigilar!", "error")
        return redirect("/")
    current_user_id = get_jwt_identity()
    try:
        peso = float(request.form.get("peso"))
        if peso < 50 or peso > 300: raise ValueError
    except:
        flash("El peso debe estar entre 50 kg y 300 kg", "error")
        return redirect("/")
    try:
        fecha = datetime.strptime(request.form.get("fecha"), "%Y-%m-%d").date()
        if fecha > date.today() or fecha < date(2000, 1, 1): raise ValueError
    except:
        flash("Fecha inválida", "error")
        return redirect("/")
    RegistroPeso.crear(current_user_id, peso, fecha)
    flash("Peso guardado correctamente", "success")
    return redirect("/")

# ---------------- REGISTER ----------------
@app.get("/register")
def register():
    """Renderiza formulario de registro"""
    return render_template("register.html")

@app.post("/register")
def register_post():
    """
    Registrar nueva cuenta
    ---
    tags:
      - Autenticación
    parameters:
      - name: email
        in: formData
        type: string
        required: true
      - name: password
        in: formData
        type: string
        required: true
      - name: altura
        in: formData
        type: number
        required: true
    """
    captcha_response = request.form.get("g-recaptcha-response")
    if not validar_captcha(captcha_response):
        flash("Captcha inválido", "error")
        return redirect("/register")
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    altura_raw = request.form.get("altura", "")
    if password.lower() in COMMON_PASSWORDS or len(password) < 8 or len(password) > 64:
        flash("Error en contraseña", "error")
        return redirect("/register")
    PASSWORD_REGEX = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    if not re.match(PASSWORD_REGEX, password):
        flash("Contraseña insegura", "error")
        return redirect("/register")
    try:
        altura = float(altura_raw)
        if altura < 50 or altura > 300: raise ValueError
    except:
        flash("Altura no válida", "error")
        return redirect("/register")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email=?", (email,))
    if cur.fetchone():
        conn.close()
        flash("Email ya registrado", "error")
        return redirect("/register")
    conn.close()
    Usuario.registrar(email, password, altura)
    flash("Cuenta creada", "success")
    return redirect("/login")

# ---------------- LOGOUT ----------------
@app.get("/logout")
def logout():
    """Cierra la sesión del usuario"""
    resp = redirect("/login")
    unset_jwt_cookies(resp)
    return resp

# ---------------- ADMIN ----------------
@app.get("/zona-admin")
@jwt_required()
def zona_admin():
    """Zona restringida para admins"""
    claims = get_jwt()
    if claims.get("rol") == "admin":
        return "<h1>ZONA DE PELIGRO ☢️</h1>"
    else:
        return redirect("/")

@app.get("/admin/registros")
@jwt_required()
def admin_registros():
    """Visualiza todos los registros (Solo Admin)"""
    claims = get_jwt()
    if claims.get("rol") != "admin": return redirect("/")
    registros = RegistroPeso.obtener_todos()
    return render_template("admin_registros.html", registros=registros)