from app.managers.cita_manager import CitaManager
from app.metrics.metrics import inc_cita_agendada

class CitasService:
    def __init__(self):
        self.citaManagerInstance = CitaManager()

    def crear_cita_service(self,paciente,medico,fecha,documento, tipoCita, motivoPaciente):
        cita = self.citaManagerInstance.agendar_cita(paciente, medico, fecha, documento, tipoCita, motivoPaciente)
        if cita:
            inc_cita_agendada()
        return cita

    def eliminar_cita_service(self,paciente,medico,fecha,documento):
        return self.citaManagerInstance.eliminar_cita(paciente, medico, fecha, documento)

    def  obtener_citas_paciente_service(self,documento):
        return self.citaManagerInstance.obtener_citas_paciente(documento)