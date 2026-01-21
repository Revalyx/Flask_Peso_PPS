🛡️ Arquitectura de Seguridad y Protocolos de Defensa
Este documento describe las medidas de seguridad técnica implementadas en Flask Peso PPS. Nuestro objetivo es garantizar la confidencialidad de los datos del usuario, siguiendo las mejores prácticas de criptografía moderna.

1. 🔐 Cifrado de Contraseñas (Hashing Avanzado)
No almacenamos contraseñas en texto plano. Utilizamos un sistema de protección robusto diseñado para resistir ataques modernos.

🧠 Algoritmo Inteligente: Scrypt
Hemos elegido Scrypt como nuestro motor de cifrado. A diferencia de otros métodos antiguos, Scrypt está diseñado para consumir memoria RAM a propósito.

¿Por qué es seguro? Porque impide que los atacantes usen tarjetas gráficas potentes (GPUs) para adivinar millones de contraseñas por segundo. Al requerir memoria, el ataque se vuelve lento y costoso.

⚙️ Configuración Criptográfica
Nuestra base de datos confirma que estamos utilizando una configuración de alta seguridad:

Factor de Coste: Muy alto (32.768 iteraciones), lo que hace que cada verificación de contraseña sea "pesada" para una máquina atacante.

Salt Único: Cada usuario tiene un código aleatorio único mezclado con su contraseña. Esto significa que dos usuarios con la misma contraseña ("123456") tendrán códigos cifrados totalmente diferentes en nuestra base de datos.

2. 🛑 Sistema Anti-Fuerza Bruta (Bloqueo de Cuenta)
Para proteger las cuentas contra robots que intentan adivinar contraseñas probando miles de combinaciones, hemos diseñado un protocolo de "Bloqueo Temporal".

⏱️ ¿Cómo funciona el "Baneo"?
El sistema vigila constantemente los intentos de acceso fallidos:

Vigilancia: Si alguien se equivoca de contraseña, el sistema anota un "fallo" en su expediente.

La Regla de los 5 Intentos: Si se detectan 5 fallos consecutivos, el sistema activa una defensa automática.

El Castigo (Time-out): La cuenta queda bloqueada durante 15 minutos. Durante este tiempo, incluso si el atacante averigua la contraseña correcta, el sistema rechazará el acceso inmediatamente sin ni siquiera comprobarla.

Rehabilitación: Pasados los 15 minutos, o si el usuario acierta la contraseña antes de llegar al límite, el contador se reinicia a cero.

3. 💉 Inmunidad a Inyección SQL
Nuestra aplicación blinda la base de datos contra el ataque más común en la web: la Inyección SQL.

🛡️ Consultas Parametrizadas
En lugar de pegar el texto del usuario directamente en las órdenes que enviamos a la base de datos, utilizamos un sistema de parámetros seguros.

El sistema trata todo lo que escribe el usuario (su email, su peso, su altura) estrictamente como datos de texto, nunca como órdenes ejecutables.

Esto significa que aunque un hacker intente escribir código malicioso en el campo de "Email", la base de datos lo guardará simplemente como un texto raro, sin ejecutarlo.

4. 🌐 Seguridad del Navegador y Sesiones
🚫 Protección XSS (Cross-Site Scripting)
Utilizamos un motor de plantillas que limpia automáticamente cualquier dato antes de mostrarlo en pantalla. Si un usuario intenta inyectar scripts o virus en su perfil, el sistema los neutraliza convirtiéndolos en texto inofensivo antes de que lleguen al navegador de otros usuarios.

🍪 Cookies Firmadas
Las "llaves" de sesión que guardamos en el navegador del usuario están firmadas criptográficamente por el servidor.

Si un usuario intenta trampear su cookie para hacerse pasar por otro (por ejemplo, cambiando su ID de usuario manualmente), el servidor detectará que el sello de seguridad está roto y expulsará la sesión inmediatamente.

5. ⚠️ Hoja de Ruta para Producción
Actualmente, el proyecto opera en modo de desarrollo académico. Para lanzarlo al mundo real, es obligatorio activar las siguientes capas extra:

HTTPS (Candado Verde): Cifrar toda la conexión para que nadie pueda leer las cookies en una red WiFi pública.

Ocultación de Secretos: Mover las claves maestras de seguridad a variables de entorno invisibles en el código fuente.

Protección de Formularios (CSRF): Añadir tokens únicos a cada formulario para asegurar que la petición viene realmente de nuestra web y no de un enlace trampa externo.
