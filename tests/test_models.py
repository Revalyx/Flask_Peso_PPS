from src.models import RegistroPeso

def test_model_to_dict():
    reg = RegistroPeso(70, "2025-11-20")
    d = reg.to_dict()

    assert d["peso"] == 70
    assert d["fecha"] == "2025-11-20"
