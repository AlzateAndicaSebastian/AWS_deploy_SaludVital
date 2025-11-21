from app.managers.resultados import Resultados

def test_agregar_y_obtener_resultados():
    r = Resultados()
    r.agregar_resultado("Ana", "glucosa", 120)
    resultados = r.obtener_resultados("Ana")
    assert len(resultados) == 1
    assert resultados[0]["examen"] == "glucosa"
    assert resultados[0]["valor"] == 120

def test_resultados_vacios():
    r = Resultados()
    assert r.obtener_resultados("Luis") == []
