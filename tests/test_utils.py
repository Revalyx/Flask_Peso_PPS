from src.utils import validar_peso

def test_validar_peso_valores_validos():
    assert validar_peso(10) is True
    assert validar_peso(75.5) is True
    assert validar_peso("60") is True

def test_validar_peso_valores_invalidos():
    assert validar_peso(0) is False
    assert validar_peso(-5) is False
    assert validar_peso("0") is False
    assert validar_peso("-10") is False

def test_validar_peso_valores_no_convertibles():
    assert validar_peso("abc") is False
    assert validar_peso("") is False
    assert validar_peso(None) is False
