import sqlite3

# PON AQUÍ EL EMAIL DEL QUE QUIERES QUE SEA EL JEFE
EMAIL_JEFE = "pepa@pepa.com" 

conn = sqlite3.connect("peso.db")
cur = conn.cursor()

# Verificamos si existe
cur.execute("SELECT id FROM users WHERE email=?", (EMAIL_JEFE,))
if cur.fetchone():
    cur.execute("UPDATE users SET rol='admin' WHERE email=?", (EMAIL_JEFE,))
    conn.commit()
    print(f"👑 ¡Hecho! El usuario {EMAIL_JEFE} ahora tiene poderes de ADMIN.")
else:
    print(f"❌ Error: El usuario {EMAIL_JEFE} no existe. Regístralo primero en la web.")

conn.close()