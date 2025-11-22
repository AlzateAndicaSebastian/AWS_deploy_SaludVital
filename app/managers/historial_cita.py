class HistorialCita:
    def __init__(self):
        self.historial = {}

    def registrar_diagnostico(self, paciente, fecha, diagnostico):
        clave = f"{paciente}_{fecha}"
        self.historial[clave] = diagnostico

    def obtener_diagnostico(self, paciente, fecha):
        clave = f"{paciente}_{fecha}"
        return self.historial.get(clave, "Sin diagnóstico registrado.")
