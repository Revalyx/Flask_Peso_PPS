import os
import sys
import subprocess
import platform

VENV_DIR = "venv"

def run(cmd):
    print(f"> {cmd}")
    subprocess.check_call(cmd, shell=True)

def get_venv_python():
    if platform.system() == "Windows":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    return os.path.join(VENV_DIR, "bin", "python")

def main():
    if not os.path.exists(VENV_DIR):
        print("Creando entorno virtual...")
        run(f'"{sys.executable}" -m venv {VENV_DIR}')

    venv_python = get_venv_python()

    if not os.path.exists(venv_python):
        print("ERROR: El entorno virtual no se creó correctamente.")
        print("En Linux asegúrese de tener instalado: python3-venv")
        sys.exit(1)

    try:
        print("Actualizando pip...")
        run(f'"{venv_python}" -m ensurepip --upgrade')
        run(f'"{venv_python}" -m pip install --upgrade pip')

        print("Instalando dependencias...")
        run(f'"{venv_python}" -m pip install -r requirements.txt')

        print("Arrancando aplicación...")
        run(f'"{venv_python}" run.py')

    except subprocess.CalledProcessError:
        print("\nERROR durante la instalación.")
        print("Puede intentar el modo manual:")
        print("  python3 -m venv venv")
        print("  source venv/bin/activate")
        print("  pip install -r requirements.txt")
        print("  python run.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
