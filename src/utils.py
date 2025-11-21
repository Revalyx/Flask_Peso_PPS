def validar_peso(valor):
    """Devuelve True si el peso es un número positivo."""
    try:
        v = float(valor)
        return v > 0
    except:
        return False
