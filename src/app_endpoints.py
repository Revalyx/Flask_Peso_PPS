from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from .models import Usuario, RegistroPeso
from datetime import datetime, date
import re

# IMPORTANTE: Asegúrate de que esta ruta a tu conexión sea correcta
from .db import get_connection 

# Crear el blueprint
api_bp = Blueprint('api', __name__)

# --- CONSTANTES DE SEGURIDAD ---
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
PASSWORD_REGEX = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
COMMON_PASSWORDS = [
    "123456", "12345678", "123456789", "password", "password123",
    "admin123", "1234", "qwerty", "qwertyui", "12345", "welcome",
    "p@ssword", "abc12345"
]

# --- LOGIN PARA ANDROID ---
@api_bp.route('/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Faltan datos JSON"}), 400
        
    email = data.get("email", "").strip()
    password = data.get("password", "")

    resultado = Usuario.login(email, password)

    if isinstance(resultado, tuple):
        user_id, rol_real = resultado
        access_token = create_access_token(identity=str(user_id), additional_claims={"rol": rol_real})
        return jsonify({
            "access_token": access_token,
            "rol": rol_real,
            "user_id": user_id
        }), 200

    return jsonify({"error": "Credenciales incorrectas"}), 401

# --- REGISTRO PARA ANDROID ---
@api_bp.route('/register', methods=['POST'])
def api_register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se han recibido datos JSON"}), 400
        
        email = data.get("email", "").strip()
        password = data.get("password", "")
        altura_raw = data.get("altura")
        rol = data.get("rol", "usuario") 

        # 1. Validación de presencia
        if not email or not password or altura_raw is None:
            return jsonify({"error": "Todos los campos son obligatorios"}), 400

        # 2. Validación de formato de Email
        if not re.match(EMAIL_REGEX, email):
            return jsonify({"error": "Formato de correo electrónico no válido"}), 400

        # 3. Validación de Password
        if password.lower() in COMMON_PASSWORDS:
            return jsonify({"error": "Esa contraseña es demasiado común y peligrosa"}), 400
        
        if len(password) < 8 or len(password) > 64:
            return jsonify({"error": "La contraseña debe tener entre 8 y 64 caracteres"}), 400

        if not re.match(PASSWORD_REGEX, password):
            return jsonify({"error": "La contraseña requiere Mayúscula, Minúscula, Número y Símbolo (@$!%*?&)"}), 400

        # 4. Validación de Altura
        try:
            altura = float(altura_raw)
            if altura < 50 or altura > 300:
                return jsonify({"error": "La altura debe estar entre 50 y 300 cm"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "La altura debe ser un número válido"}), 400

        # 5. Lógica de Base de Datos (Anti-Enumeración)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email=?", (email,))
        if cur.fetchone():
            conn.close()
            # Mensaje genérico para seguridad
            return jsonify({"error": "No se ha podido completar el registro con estos datos"}), 400
        conn.close()

        # 6. Registro real
        Usuario.registrar(email, password, altura, rol)
        return jsonify({"message": "Cuenta creada correctamente"}), 201

    except Exception as e:
        print(f"DEBUG Error Crítico en Registro: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

# --- REGISTRAR PESO PARA ANDROID ---
@api_bp.route('/registro_peso', methods=['POST'])
@jwt_required()
def api_registrar_peso():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or "peso" not in data:
        return jsonify({"error": "Faltan datos de peso"}), 400
        
    try:
        # 1. Validación de Peso
        peso = round(float(data.get("peso")), 2)
        if peso < 30.0 or peso > 500.0: 
            return jsonify({"error": "El peso debe estar entre 30kg y 500kg"}), 400

        # 2. Validación de Fecha
        fecha_str = data.get("fecha")
        if fecha_str:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            if fecha > date.today():
                return jsonify({"error": "No puedes registrar fechas futuras"}), 400
        else:
            fecha = date.today()

        # 3. Guardar en DB
        RegistroPeso.crear(current_user_id, peso, fecha)
        return jsonify({"message": "Peso registrado correctamente"}), 201

    except ValueError:
        return jsonify({"error": "Formato de peso o fecha incorrecto"}), 400
    except Exception as e:
        print(f"DEBUG: Error en registro_peso -> {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

# --- OBTENER PESOS ---
@api_bp.route('/mis_pesos', methods=['GET'])
@jwt_required()
def api_obtener_pesos():
    current_user_id = get_jwt_identity()
    registros = RegistroPeso.obtener_por_usuario(current_user_id)
    
    lista_pesos = [
        {"id": r[0], "peso": r[1], "fecha": r[2]} 
        for r in registros
    ]
    return jsonify(lista_pesos), 200