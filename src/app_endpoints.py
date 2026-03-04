from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .models import Usuario, RegistroPeso
from datetime import datetime, date
# Crear el blueprint
api_bp = Blueprint('api', __name__)

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
    data = request.get_json()
    if not data:
        return jsonify({"error": "Faltan datos"}), 400
    
    email = data.get("email")
    password = data.get("password")
    altura = data.get("altura")

    if not email or not password or not altura:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    try:
        # Registramos al usuario (asegurándonos de que altura sea float)
        Usuario.registrar(email, password, float(altura))
        return jsonify({"message": "Usuario creado correctamente"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- API: REGISTRAR PESO ---
@api_bp.route('/registro_peso', methods=['POST'])
@jwt_required()
def api_registrar_peso():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or "peso" not in data:
        return jsonify({"error": "Faltan datos"}), 400
        
    try:
        # Validación de Peso
        peso = float(data.get("peso"))
        
        # Validación de Fecha (Aquí es donde usas el import que pusiste arriba)
        fecha_texto = data.get("fecha")
        if fecha_texto:
            # datetime.strptime convierte "2026-03-04" en un objeto que la DB entiende
            fecha_objeto = datetime.strptime(fecha_texto, "%Y-%m-%d").date()
        else:
            fecha_objeto = date.today()

        # Guardar en la base de datos
        RegistroPeso.crear(current_user_id, peso, fecha_objeto)
        return jsonify({"message": "Peso registrado correctamente"}), 201

    except NameError:
        return jsonify({"error": "Error en el servidor: Falta el import de datetime"}), 500
    except ValueError:
        return jsonify({"error": "Formato de fecha o peso incorrecto"}), 400
    except Exception as e:
        print(f"Error detectado: {e}")
        return jsonify({"error": str(e)}), 500
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or "peso" not in data:
        return jsonify({"error": "Faltan datos de peso"}), 400
        
    try:
        # 1. Validación de Peso
        peso = float(data.get("peso"))
        if peso < 30 or peso > 500:
            return jsonify({"error": "Peso fuera de rango (30-500kg)"}), 400

        # 2. Validación de Fecha (Usando el objeto date de Python)
        fecha_recibida = data.get("fecha")
        
        if fecha_recibida:
            # Convertimos el texto "2026-03-04" en un objeto fecha real
            fecha_final = datetime.strptime(fecha_recibida, "%Y-%m-%d").date()
            
            if fecha_final > date.today():
                return jsonify({"error": "No puedes registrar fechas futuras"}), 400
        else:
            fecha_final = date.today()

        # 3. Guardar en la Base de Datos
        # RegistroPeso.crear espera (user_id, peso, objeto_fecha)
        RegistroPeso.crear(current_user_id, peso, fecha_final)
        
        return jsonify({"message": "Peso registrado correctamente"}), 201

    except ValueError:
        # Esto saltará si 'peso' no es número o 'fecha' no tiene formato YYYY-MM-DD
        return jsonify({"error": "Formato de peso o fecha incorrecto"}), 400
    except Exception as e:
        # Esto nos dirá en la terminal si hay algún otro problema
        print(f"Error interno: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or "peso" not in data:
        return jsonify({"error": "Faltan datos de peso"}), 400
        
    try:
        # 1. Validación de Peso (Aceptamos hasta 500 inclusive)
        try:
            # Convertimos a float y redondeamos a 2 decimales para evitar problemas de precisión
            peso = round(float(data.get("peso")), 2)
            
            if peso < 30.0 or peso > 500.0: 
                return jsonify({"error": "El peso debe estar entre 30kg y 500kg"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "El peso debe ser un número válido"}), 400

        # 2. Validación de Fecha
        fecha_str = data.get("fecha")
        if fecha_str:
            try:
                # Si viene como string desde la App, lo convertimos
                if isinstance(fecha_str, str):
                    fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
                else:
                    fecha = date.today()
                    
                if fecha > date.today():
                    return jsonify({"error": "No puedes registrar fechas futuras"}), 400
                if fecha < date(2000, 1, 1):
                    return jsonify({"error": "Fecha demasiado antigua"}), 400
            except ValueError:
                return jsonify({"error": "Formato de fecha inválido"}), 400
        else:
            fecha = date.today()

        # 3. Guardar con Captura de Errores de BD
        try:
            RegistroPeso.crear(current_user_id, peso, fecha)
            return jsonify({"message": "Peso registrado correctamente"}), 201
        except Exception as db_error:
            # ESTO ES CLAVE: Verás el error real en tu terminal (Ej: Tabla no existe, columna llena, etc.)
            print(f"DEBUG: Error al insertar en DB -> {db_error}")
            return jsonify({"error": f"Error en base de datos: {str(db_error)}"}), 500

    except Exception as e:
        print(f"DEBUG: Error general en el endpoint -> {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@api_bp.route('/mis_pesos', methods=['GET'])
@jwt_required()
def api_obtener_pesos():
    current_user_id = get_jwt_identity()
    # Asumiendo que tu modelo tiene esta función
    registros = RegistroPeso.obtener_por_usuario(current_user_id)
    
    # Formateamos para JSON: lista de diccionarios
    lista_pesos = [
        {"id": r[0], "peso": r[1], "fecha": r[2]} 
        for r in registros
    ]
    return jsonify(lista_pesos), 200        