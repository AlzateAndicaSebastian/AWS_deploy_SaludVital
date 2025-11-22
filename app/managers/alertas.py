class Alertas:
    def __init__(self, umbrales=None):
        self.umbrales = umbrales or {
            "glucosa": 110,
            "presion": 140
        }

    def verificar(self, examen, valor):
        if examen in self.umbrales:
            return valor > self.umbrales[examen]
        return False

    def generar_alertas(self, resultados_paciente):
        alertas = []
        for resultado in resultados_paciente:
            if self.verificar(resultado["examen"], resultado["valor"]):
                alertas.append(f"Alerta: {resultado['examen']} = {resultado['valor']}")
        return alertas
