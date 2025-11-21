from app.managers.historial_cita import HistorialCita

def test_registrar_y_obtener_diagnostico():
    hc = HistorialCita()
    hc.registrar_diagnostico("Ana", "2025-04-10", "Hipertensión")
    diagnostico = hc.obtener_diagnostico("Ana", "2025-04-10")
    assert diagnostico == "Hipertensión"

def test_diagnostico_no_encontrado():
    hc = HistorialCita()
    assert hc.obtener_diagnostico("Luis", "2025-04-12") == "Sin diagnóstico registrado."
