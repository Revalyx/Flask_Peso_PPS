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


## ⚙️ Ejecución en local (recomendada)

Esta aplicación está pensada exclusivamente para ejecutarse en **entorno local**.

### Opción rápida (Windows / Linux / macOS)

#### 1. Descarga el proyecto como ZIP desde GitHub y descomprímelo

#### 2. Abre una terminal en la carpeta del proyecto

#### 3. Ejecuta el siguiente comando

```
python start.py
```

> #### El script se encarga automáticamente de:
>
> * Crear el entorno virtual
>
> * Instalar las dependencias
>
> * Arrancar la aplicación

La aplicación estará disponible en:

```txt
http://127.0.0.1:5000
```

Para detener el servidor, pulsa **CTRL + C.**


## ℹ️ Notas

La aplicación utiliza una SECRET_KEY fija para uso académico (En producción no la hardcodearíamos)

**No está preparada para despliegue en producción**


**Proyecto orientado a prácticas y aprendizaje**

