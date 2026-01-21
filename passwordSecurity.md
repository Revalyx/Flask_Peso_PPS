# 🛡️ Arquitectura de Seguridad y Protocolos de Defensa

Este documento describe las medidas de seguridad técnica implementadas en **Flask Peso PPS**. Nuestro objetivo es garantizar la confidencialidad de los datos del usuario, siguiendo las mejores prácticas de criptografía moderna.

---


## 1. 🔐 Cifrado de Contraseñas (Hashing Avanzado)

Para el almacenamiento de credenciales, hemos descartado algoritmos de hashing de propósito general (como SHA-256 o MD5) en favor de Scrypt, una función de derivación de claves diseñada específicamente para ser costosa en términos de hardware.

### 1.1. Justificación Técnica (Memory Hardness)
La principal vulnerabilidad de los hashes tradicionales es que pueden calcularse extremadamente rápido en hardware paralelo (GPUs/ASICs). Scrypt mitiga esto imponiendo un coste de memoria y un coste de CPU. Resistencia ASIC: Al requerir mover grandes bloques de memoria RAM para calcular un solo hash, invalidamos la ventaja de los atacantes que usan granjas de minería o hardware dedicado, ya que este hardware suele tener muy poca memoria por núcleo.

### 1.2. Parámetros Criptográficos en Producción
Nuestra implementación utiliza los siguientes parámetros de coste, ajustados para equilibrar seguridad y usabilidad (latencia < 200ms por login legítimo):


| Parámetro | Valor | Significado |
| :--- | :--- | :--- |
| **Algoritmo** | Scrypt | Resistente a ASICs/GPUs |
| **Coste (N)** | 32.768 | Iteraciones muy altas (verificación "pesada") |
| **Bloque (r)** | 8 | Factor de memoria estándar |
| **Salt** | Único | Un código aleatorio distinto para cada usuario |

### 1.3. Implementación en Código

La seguridad se delega en la librería probada werkzeug.security. El siguiente fragmento muestra cómo se aplica el hash automáticamente antes de persistir el usuario:

```python
# Archivo: src/models.py

from werkzeug.security import generate_password_hash

password_hashed = generate_password_hash(password)

cur.execute(""" INSERT INTO users (email, password, altura) VALUES (?, ?, ?) """, (email, password_hashed, altura))

```

---

## 2. 🛑 Sistema Anti-Fuerza Bruta (Bloqueo de Cuenta)

Para proteger las cuentas contra robots que intentan adivinar contraseñas probando miles de combinaciones, hemos diseñado un protocolo de **"Bloqueo Temporal"**.

### ⏱️ ¿Cómo funciona el protocolo de Baneo?

1.  **👁️ Vigilancia Constante**
    El sistema no tiene "amnesia". Cada vez que se produce un error de autenticación, este no se descarta; se registra persistentemente en la base de datos asociado al perfil del usuario.
    * Esto nos permite detectar ataques lentos que ocurren a lo largo de varios minutos u horas, ya que el contador de fallos se mantiene guardado hasta que haya un login exitoso.

2.  **⚠️ La Regla de los 5 Intentos**
   Hemos configurado un "disparador" de seguridad ajustado a **5 intentos**.
    * **¿Por qué 5?** Es el equilibrio perfecto: ofrece margen suficiente para que un usuario legítimo se equivoque al escribir (dedos torpes), pero es una ventana demasiado pequeña para que un robot de fuerza bruta tenga éxito adivinando una contraseña compleja. Al cruzar este límite, el sistema asume que se trata de un ataque automatizado.
    


```python
# Lógica de Protección (src/models.py)

# 1. Comprobar si ya está baneado antes de validar contraseña

if usuario.bloqueado_hasta and usuario.bloqueado_hasta > datetime.now():

    return "BLOCKED"  # Rechazo inmediato

# 2. Si la contraseña falla, aumentar contador

if not check_password_hash(usuario.password, password_input):

    usuario.intentos_fallidos += 1
    
    # Si llega al límite de 5 fallos -> BANEO

    if usuario.intentos_fallidos >= 5:

        usuario.bloqueado_hasta = datetime.now() + timedelta(minutes=15)
        
    db.session.commit()

    return "WRONG_PASS"

```

3.  **⏳ El Castigo (Time-out)**
   La cuenta queda **bloqueada durante 15 minutos**.
    * **Defensa de Recursos:** Esta fase no solo protege la contraseña, sino también el servidor. Al rechazar la petición chequeando simplemente una fecha (`bloqueado_hasta`), evitamos ejecutar el cálculo pesado de *Scrypt*. Esto significa que aunque un atacante nos bombardee con millones de peticiones, el servidor las descartará en microsegundos sin saturarse.

4.  **✅ Rehabilitación**
    El sistema es capaz de "curarse" solo sin intervención de un administrador.
    * **Reinicio por Éxito:** Si el usuario acierta su contraseña antes de llegar al límite (ej. al 4º intento), el sistema asume que fue un error humano y resetea los contadores a cero inmediatamente.
    * **Expiración del Castigo:** Pasados los 15 minutos, la restricción temporal caduca automáticamente, permitiendo al usuario legítimo volver a intentarlo sin tener que contactar con soporte.

```sql

# Archivo: src/models.py

-- Estructura de base de datos para soporte de bloqueo

ALTER TABLE users ADD COLUMN intentos_fallidos INTEGER DEFAULT 0;

ALTER TABLE users ADD COLUMN bloqueado_hasta DATETIME DEFAULT NULL;

```
---



