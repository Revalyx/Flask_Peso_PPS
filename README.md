# Proyecto Flask Peso

[![Coverage Status](https://coveralls.io/repos/github/Revalyx/Flask_Peso_PPS/badge.svg?branch=main)](https://coveralls.io/github/Revalyx/Flask_Peso_PPS?branch=main)

Aplicación web desarrollada con Flask para el registro y seguimiento del peso corporal de los usuarios.
Permite gestionar usuarios, almacenar registros históricos de peso y calcular indicadores básicos como el IMC.

## 🚀 Funcionalidades

- Registro y autenticación de usuarios

- Registro de peso con validaciones

- Historial de pesos por usuario

- Cálculo automático del IMC

- Mensajes de error y confirmación

- Sistema de sesiones

- Tests automatizados con cobertura

## 🛠️ Tecnologías

- **Python 3**  
   Lenguaje de programación principal del proyecto. Se utiliza para desarrollar la lógica de la aplicación, gestionar los datos, realizar validaciones y coordinar el funcionamiento general del sistema.

- **Flask**  
  Framework web ligero empleado para construir la aplicación web. Se encarga de la gestión de rutas, el sistema de plantillas, las sesiones de usuario y la comunicación entre el cliente y el servidor.

- **SQLite**  
  Base de datos relacional ligera integrada en el proyecto. Permite almacenar de forma persistente la información de los usuarios y los registros de peso sin necesidad de un servidor de base de datos externo.

- **pytest**  
  Framework de pruebas automatizadas utilizado para verificar el correcto funcionamiento de la aplicación. Facilita la creación de tests que validan la lógica del sistema y ayudan a prevenir regresiones.

- **coverage / coveralls**  
  Herramientas utilizadas para medir y visualizar la cobertura de código de los tests. `coverage` calcula qué partes del código están siendo ejecutadas durante las pruebas, mientras que `coveralls` permite publicar estos resultados de forma visual en el repositorio.

- **Werkzeug (Security)**
  Librería fundamental para la seguridad de la aplicación. Se encarga de hashear las contraseñas utilizando el algoritmo Scrypt y gestiona la generación automática del **salt** para cada usuario, asegurando un almacenamiento irreversible y robusto de las credenciales.
  
- **Google reCAPTCHA v2**
  Servicio de protección contra bots implementado en el formulario de registro. Se valida en el servidor comunicándose con la API de Google mediante la librería `requests` para asegurar que el usuario es humano antes de procesar cualquier dato.

- **HSTS & CSP (Cabeceras de Seguridad)**
  Implementación de *HTTP Strict Transport Security* para forzar conexiones seguras y *Content Security Policy* para prevenir ataques XSS. Estas cabeceras se inyectan en cada respuesta del servidor mediante un middleware (`@app.after_request`), controlando rigurosamente los orígenes permitidos de scripts y estilos.

- **ModSecurity + OWASP CRS (WAF)**
   Cortafuegos de aplicaciones web (WAF) desplegado en un contenedor Docker con Nginx. Actúa como proxy inverso interceptando todo el tráfico entrante y bloqueando peticiones maliciosas (como inyecciones SQL, XSS y escaneos de vulnerabilidades) mediante el conjunto de reglas estándar de OWASP (Core Rule Set), blindando la aplicación antes de que las peticiones toquen el servidor Flask.
  
## ⚙️ Ejecución con Docker y WAF (Recomendada)

Esta aplicación está diseñada para ejecutarse en contenedores **Docker**, protegida por un **WAF (ModSecurity + Nginx)** que filtra ataques.

### Requisitos previos

- Tener Docker instalado y corriendo.

- Linux: Asegúrate de tener permisos (o usa sudo antes de los comandos).

### Instrucciones de Despliegue

- **ANTES DE EMPEZAR CON EL PROCESO, ES NECESARIO TENER INSTALADO Y ABIERTO DOCKER DESKTOP**
  
#### 1. Abre una terminal en la carpeta del proyecto

#### 2. Construye la imagen de la aplicación:

```
docker build -t mi-app-flask .
```
#### 3. Despliega la infraestructura: Copia y ejecuta estos comandos en orden para levantar la red, la app y el WAF.

```
docker network create red-hacker
```
```
docker run -d -p 5000:5000 --name la-app --network red-hacker -e FLASK_RUN_HOST=0.0.0.0 mi-app-flask
```
```
docker run -d -p 80:80 --name el-waf --network red-hacker -e BACKEND=http://la-app:5000 -e SERVER_NAME=localhost owasp/modsecurity-crs:3-nginx
```

### Acceso y Pruebas

- Entrar a la web: Abre http://localhost en tu navegador.

### Limpiar y Parar

```docker rm -f la-app el-waf ```

## ℹ️ Notas

La aplicación utiliza una SECRET_KEY fija para uso académico (En producción no la hardcodearíamos)

**No está preparada para despliegue en producción**


**Proyecto orientado a prácticas y aprendizaje**





