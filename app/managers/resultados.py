class Resultados:
    def __init__(self):
        self.resultados = {}

    def agregar_resultado(self, paciente, examen, valor):
        if paciente not in self.resultados:
            self.resultados[paciente] = []
        self.resultados[paciente].append({"examen": examen, "valor": valor})

    def obtener_resultados(self, paciente):
        return self.resultados.get(paciente, [])
