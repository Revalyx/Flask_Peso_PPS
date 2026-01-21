# 🛡️ Arquitectura de Seguridad y Protocolos de Defensa

Este documento describe en profundidad las medidas de seguridad técnica implementadas en **Flask Peso PPS**. El objetivo es garantizar la confidencialidad, integridad y disponibilidad de los datos del usuario, siguiendo las mejores prácticas de OWASP y criptografía moderna.

---

## 1. Cifrado de Contraseñas (Hashing Avanzado)

No almacenamos contraseñas en texto plano. Utilizamos un esquema de **hashing unidireccional** robusto resistente a ataques por hardware dedicado (ASIC/GPU).

### Algoritmo: Scrypt
Elegimos **Scrypt** sobre alternativas como *PBKDF2* o *BCrypt* debido a su **dureza de memoria** (Memory Hardness). Scrypt requiere una cantidad significativa de RAM para calcular cada hash, lo que neutraliza la ventaja de los atacantes que utilizan tarjetas gráficas (GPUs) para romper contraseñas masivamente.

### Configuración Criptográfica
Nuestra implementación (vía `Werkzeug`) utiliza los siguientes parámetros de coste, verificables en la base de datos:

* **Método:** `scrypt`
* **Factor de Coste (N):** `32768` (2^15 iteraciones).
* **Tamaño de Bloque (r):** `8`.
* **Paralelización (p):** `1`.

> **Formato de Almacenamiento:**
> En la base de datos, el hash se guarda con el formato:
> `scrypt:32768:8:1$<salt_aleatorio>$<hash_resultante>`
>
> *El **Salt** es único por usuario, impidiendo ataques de Rainbow Tables (tablas precomputadas).*

---

## 2. Sistema Anti-Fuerza Bruta (Account Locking)

Para proteger las cuentas contra intentos de adivinanza de contraseñas automatizados, implementamos un sistema de bloqueo temporal inteligente.

### Esquema de Base de Datos
Se añaden dos columnas de control a la tabla `users` para gestionar el estado de seguridad de cada cuenta:

```sql
ALTER TABLE users ADD COLUMN failed_attempts INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN locked_until DATETIME DEFAULT NULL;
```
Algoritmo de Defensa
El flujo de autenticación (/login) sigue una lógica estricta de "Check-Lock-Verify":

Fase de Verificación de Bloqueo: Antes de verificar la contraseña, el sistema consulta locked_until.

Si la fecha actual < locked_until: Se rechaza la petición inmediatamente lanzando un error de "Cuenta bloqueada temporalmente". No se procesa el hash (ahorrando CPU).

Fase de Validación:

Si la contraseña es INCORRECTA:

Se incrementa el contador failed_attempts.

Regla de Baneo: Si failed_attempts >= 5, se establece locked_until a 15 minutos en el futuro.

Si la contraseña es CORRECTA:

Se restablecen failed_attempts = 0 y locked_until = NULL.

Se permite el acceso.

3. 💉 Prevención de Inyección SQL (SQLi)
La aplicación es inmune a la inyección SQL clásica gracias al uso estricto de Consultas Parametrizadas en la capa de acceso a datos.

Implementación
En lugar de concatenar cadenas (lo cual es vulnerable), utilizamos los marcadores de posición (?) nativos del driver sqlite3 de Python. Esto asegura que el motor de base de datos trate los inputs del usuario estrictamente como datos literales, nunca como código ejecutable.

Código Seguro (src/models.py):

Python

# ✅ CORRECTO: El motor escapa automáticamente el input
cur.execute("INSERT INTO users ... VALUES (?, ?, ?)", (email, password, altura))

# ❌ INCORRECTO (Vulnerable): Nunca usado en este proyecto
# cur.execute(f"INSERT INTO users ... VALUES ('{email}', ...)")
4. 🌐 Seguridad Frontend y Sesiones
Protección contra XSS (Cross-Site Scripting)
Utilizamos el motor de plantillas Jinja2, que está configurado por defecto con Auto-Escaping.

Cualquier dato renderizado en el HTML (ej. {{ usuario.nombre }}) se escapa automáticamente.

Esto convierte caracteres peligrosos (<, >, &) en entidades HTML seguras, impidiendo la inyección de scripts maliciosos en el navegador de la víctima.

Gestión de Sesiones
Las sesiones de usuario se gestionan mediante cookies firmadas criptográficamente (Secure Cookies).

Integridad: La cookie contiene una firma generada con la SECRET_KEY del servidor. Si un usuario intenta manipular el contenido de su cookie (ej. cambiar su user_id), la firma será inválida y el servidor rechazará la sesión.

5. ⚠️ Notas para Despliegue (Roadmap)
Actualmente, el proyecto está configurado para un entorno de desarrollo/académico. Para un despliegue en producción (Live), se deben aplicar las siguientes mejoras mandatorias:

HTTPS (TLS/SSL): Obligatorio para cifrar el tráfico en tránsito y proteger la cookie de sesión.

Variables de Entorno: La SECRET_KEY no debe estar hardcodeada en el código (src/app.py), sino cargarse desde un archivo .env no versionado.

Flag Secure en Cookies: Configurar SESSION_COOKIE_SECURE = True para que las cookies solo viajen por HTTPS.

Protección CSRF: Implementar tokens anti-CSRF (via Flask-WTF) en todos los formularios POST.
