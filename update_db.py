import sqlite3

def actualizar_bd():
    print("🔧 Actualizando base de datos...")
    conn = sqlite3.connect("peso.db")
    cur = conn.cursor()
    
    try:
        # Añadimos la columna 'rol' y por defecto todos serán 'user'
        cur.execute("ALTER TABLE users ADD COLUMN rol TEXT DEFAULT 'user'")
        conn.commit()
        print("✅ ¡ÉXITO! Columna 'rol' añadida. Todos son 'user' por defecto.")
    except sqlite3.OperationalError:
        print("ℹ️ La columna 'rol' ya existía, no hace falta tocar nada.")
        
    conn.close()

if __name__ == "__main__":
    actualizar_bd()