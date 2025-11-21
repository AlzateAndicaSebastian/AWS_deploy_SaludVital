from app.managers.alertas import Alertas

def test_generar_alertas_sin_alertas():
    a = Alertas()
    resultados = [{"examen": "glucosa", "valor": 100}]
    alertas = a.generar_alertas(resultados)
    assert alertas == []

def test_generar_alertas_con_alertas():
    a = Alertas()
    resultados = [
        {"examen": "glucosa", "valor": 120},
        {"examen": "presion", "valor": 145}
    ]
    alertas = a.generar_alertas(resultados)
    assert len(alertas) == 2
    assert "glucosa" in alertas[0]
    assert "presion" in alertas[1]
