import os
import subprocess
import sys
import platform

VENV_DIR = "venv"

def run(cmd):
    print(f"> {cmd}")
    subprocess.check_call(cmd, shell=True)

def main():
    python_cmd = sys.executable

    # 1. Crear venv si no existe
    if not os.path.isdir(VENV_DIR):
        print("Creando entorno virtual...")
        run(f"{python_cmd} -m venv {VENV_DIR}")

    # 2. Determinar python dentro del venv
    if platform.system() == "Windows":
        venv_python = os.path.join(VENV_DIR, "Scripts", "python")
    else:
        venv_python = os.path.join(VENV_DIR, "bin", "python")

    # 3. Actualizar pip
    run(f"{venv_python} -m pip install --upgrade pip")

    # 4. Instalar dependencias
    run(f"{venv_python} -m pip install -r requirements.txt")

    # 5. Ejecutar la app
    try:
        run(f"{venv_python} run.py")
    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")


if __name__ == "__main__":
    main()
