from flask import Flask, request, session, redirect, render_template_string
import json
from .db import init_db, get_connection
from .models import Usuario, RegistroPeso

app = Flask(__name__)
app.secret_key = "super_secret_key"

init_db()

# -------------------------- UI MEJORADA (ESTILO FINAL) --------------------------
PAGE_HEADER = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Peso App</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --bg: #0f172a;
            --card-bg: #1e293b;
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --danger: #ef4444;
            --success: #4ade80;
            --warning: #fbbf24;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg);
            color: var(--text);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            width: 100%;
            max-width: 800px;
            background: var(--card-bg);
            padding: 2.5rem;
            border-radius: 24px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            animation: fadeIn 0.5s ease-out;
        }

        h2 {
            text-align: center;
            margin-bottom: 1.5rem;
            font-weight: 800;
            background: linear-gradient(to right, #818cf8, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2rem;
        }

        input {
            width: 100%;
            padding: 1rem;
            margin-bottom: 1rem;
            background: #334155;
            border: 2px solid transparent;
            border-radius: 12px;
            color: white;
            font-size: 1rem;
            transition: all 0.3s;
        }

        input:focus {
            outline: none;
            border-color: var(--primary);
            background: #475569;
        }

        button {
            width: 100%;
            padding: 1rem;
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: white;
            border: none;
            border-radius: 12px;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            margin-top: 0.5rem;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(99, 102, 241, 0.3);
        }

        .btn-secondary {
            background: #334155;
            color: var(--text-muted);
        }
        .btn-secondary:hover {
            background: #475569;
            color: white;
        }

        a {
            display: block;
            text-align: center;
            margin-top: 1.5rem;
            color: var(--text-muted);
            text-decoration: none;
            font-size: 0.9rem;
            transition: color 0.2s;
        }

        a:hover { color: var(--primary); }

        /* Dashboard Grid actualizado a 3 columnas */
        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 15px;
            margin-bottom: 25px;
        }
        
        .stat-card {
            background: #334155;
            padding: 20px;
            border-radius: 16px;
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }

        .stat-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #818cf8;
        }
        
        /* Clase especial para texto más pequeño en la caja de estado si es largo */
        .stat-text-sm {
            font-size: 1.2rem;
        }

        .stat-label {
            font-size: 0.9rem;
            color: var(--text-muted);
            margin-top: 5px;
        }

        .list-container {
            margin-top: 20px;
            max-height: 250px;
            overflow-y: auto;
            margin-bottom: 30px;
            background: rgba(0,0,0,0.1);
            border-radius: 12px;
            padding: 10px;
        }

        .peso-item {
            display: flex;
            justify-content: space-between;
            padding: 12px;
            border-bottom: 1px solid #334155;
            color: var(--text-muted);
        }
        
        .peso-item span:last-child {
            color: var(--text);
            font-weight: 600;
        }

        /* Collapsible Details */
        details {
            margin-top: 20px;
            border-top: 1px solid #334155;
            padding-top: 15px;
            margin-bottom: 15px;
        }
        summary {
            color: var(--text-muted);
            cursor: pointer;
            font-size: 0.9rem;
            list-style: none;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        summary:hover { color: var(--primary); }
        summary::after { content: '+'; font-weight: bold; }
        details[open] summary::after { content: '-'; }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
"""

PAGE_FOOTER = """
</body>
</html>
"""

# -------------------------- Rutas --------------------------

@app.get("/login")
def login():
    custom_style = """<style>.container { max-width: 400px !important; }</style>"""
    return render_template_string(PAGE_HEADER + custom_style + """
    <div class="container">
        <h2>Bienvenido</h2>
        <form method="POST">
            <input name="email" placeholder="Correo electrónico" required>
            <input type="password" name="password" placeholder="Contraseña" required>
            <button>Entrar</button>
        </form>
        <a href="/register">¿No tienes cuenta? Regístrate</a>
    </div>
    """ + PAGE_FOOTER)

@app.post("/login")
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")
    user_id = Usuario.login(email, password)
    
    if not user_id:
        custom_style = """<style>.container { max-width: 400px !important; }</style>"""
        return render_template_string(PAGE_HEADER + custom_style + """
        <div class="container" style="text-align: center;">
            <h2 style="color: var(--danger);">Error</h2>
            <p style="color: var(--text-muted); margin-bottom: 20px;">Credenciales incorrectas.</p>
            <a href="/login" style="color: white; background: #334155; padding: 10px; border-radius: 8px;">Intentar de nuevo</a>
        </div>
        """ + PAGE_FOOTER)

    session["user_id"] = user_id
    return redirect("/")

@app.get("/register")
def register():
    custom_style = """<style>.container { max-width: 400px !important; }</style>"""
    return render_template_string(PAGE_HEADER + custom_style + """
    <div class="container">
        <h2>Nueva Cuenta</h2>
        <form method="POST">
            <input name="email" placeholder="Correo electrónico" required>
            <input type="password" name="password" placeholder="Contraseña" required>
            <input type="number" step="0.01" name="altura" placeholder="Altura (cm)" required>
            <button>Registrarse</button>
        </form>
        <a href="/login">Ya tengo cuenta</a>
    </div>
    """ + PAGE_FOOTER)

@app.post("/register")
def register_post():
    email = request.form.get("email")
    password = request.form.get("password")
    altura = request.form.get("altura")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email=?", (email,))
    if cur.fetchone():
        conn.close()
        return "El usuario ya existe <a href='/register'>Volver</a>"
    conn.close()

    user_id = Usuario.registrar(email, password, altura)
    session["user_id"] = user_id
    return redirect("/")

@app.get("/")
def home():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    
    registros = RegistroPeso.obtener_por_usuario(user_id)
    altura = Usuario.get_altura(user_id)
    
    labels = [r[2] for r in registros][::-1]
    data = [r[1] for r in registros][::-1]
    
    ultimo_peso = registros[0][1] if registros else 0
    
    # LOGICA IMC Y ESTADO
    imc = 0
    estado = "---"
    color_estado = "#94a3b8" # Gris por defecto

    if altura and ultimo_peso:
        imc = round(ultimo_peso / ((altura/100)**2), 2)
        
        if imc < 18.5:
            estado = "Bajo Peso"
            color_estado = "#fbbf24" # Amarillo
        elif imc < 25:
            estado = "Normopeso"
            color_estado = "#4ade80" # Verde (Voy fino)
        elif imc < 30:
            estado = "Sobrepeso"
            color_estado = "#fb923c" # Naranja
        else:
            estado = "Obesidad"
            color_estado = "#ef4444" # Rojo

    content_html = """
    <div class="container">
        <h2>Tu Progreso</h2>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{{ peso_actual }} kg</div>
                <div class="stat-label">Peso Actual</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ imc }}</div>
                <div class="stat-label">IMC</div>
            </div>
            <div class="stat-card">
                <div class="stat-value stat-text-sm" style="color: {{ color_estado }}">{{ estado }}</div>
                <div class="stat-label">Estado</div>
            </div>
        </div>

        <form method="POST" action="/registro" style="display: flex; gap: 15px; align-items: center; background: #334155; padding: 15px; border-radius: 12px;">
            <div style="flex-grow: 1;">
                <label style="font-size:0.8rem; color:var(--text-muted);">Nuevo registro:</label>
                <div style="display:flex; gap:10px; margin-top:5px;">
                    <input type="number" step="0.01" name="peso" placeholder="Peso (kg)" required style="margin-bottom:0;">
                    <input type="date" name="fecha" required style="margin-bottom:0;">
                </div>
            </div>
            <button type="submit" style="margin-top:18px; width: auto; padding: 1rem 1.5rem;">+</button>
        </form>

        <h3 style="margin-top: 30px; font-size: 1.1rem; color: var(--text-muted);">Últimos registros</h3>
        <div class="list-container">
            {% for r in registros %}
            <div class="peso-item">
                <span>{{ r[2] }}</span>
                <span>{{ r[1] }} kg</span>
            </div>
            {% else %}
            <p style="text-align: center; color: var(--text-muted); margin-top: 20px;">Sin registros aún.</p>
            {% endfor %}
        </div>

        <h3 style="margin-bottom: 15px; font-size: 1.1rem; color: var(--text-muted);">Evolución</h3>
        <canvas id="weightChart" height="120" style="margin-bottom: 30px;"></canvas>

        <details>
            <summary>Mis Datos / Configuración</summary>
            <div style="margin-top: 15px;">
                <form method="POST" action="/update_height">
                    <label style="color: var(--text-muted); font-size: 0.8rem; margin-bottom: 5px; display:block;">Actualizar Altura (cm):</label>
                    <div style="display: flex; gap: 10px;">
                        <input type="number" step="0.01" name="altura" value="{{ altura }}" required style="margin-bottom:0;">
                        <button type="submit" class="btn-secondary" style="margin-top:0; width: auto;">Guardar</button>
                    </div>
                </form>
            </div>
        </details>
        
        <a href="/logout" style="color: var(--danger); margin-top: 20px;">Cerrar sesión</a>

    </div>

    <script>
        const ctx = document.getElementById('weightChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: {{ labels | tojson }},
                datasets: [{
                    label: 'Peso (kg)',
                    data: {{ data | tojson }},
                    borderColor: '#818cf8',
                    backgroundColor: 'rgba(129, 140, 248, 0.2)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 5,
                    pointBackgroundColor: '#c084fc'
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    x: { 
                        grid: { display: false },
                        ticks: { color: '#94a3b8' }
                    },
                    y: { 
                        grid: { color: '#334155' },
                        ticks: { color: '#94a3b8' }
                    }
                }
            }
        });
    </script>
    """
    
    return render_template_string(
        PAGE_HEADER + content_html + PAGE_FOOTER, 
        registros=registros, 
        labels=labels, 
        data=data, 
        peso_actual=ultimo_peso, 
        imc=imc,
        altura=altura,
        estado=estado,
        color_estado=color_estado
    )

@app.post("/registro")
def registrar_peso():
    if "user_id" not in session:
        return redirect("/login")
    RegistroPeso.crear(session["user_id"], request.form.get("peso"), request.form.get("fecha"))
    return redirect("/")

@app.post("/update_height")
def update_height():
    if "user_id" not in session:
        return redirect("/login")
    
    nueva_altura = request.form.get("altura")
    if nueva_altura:
        Usuario.actualizar_altura(session["user_id"], nueva_altura)
        
    return redirect("/")

@app.get("/logout")
def logout():
    session.clear()
    return redirect("/login")