from app.managers.cita_manager import CitaManager

class CitasService:
    def __init__(self):
        self.citaManagerInstance = CitaManager()

    def crear_cita_service(self,paciente,medico,fecha,documento, tipoCita, motivoPaciente):
        return self.citaManagerInstance.agendar_cita(paciente, medico, fecha, documento, tipoCita, motivoPaciente)

    def eliminar_cita_service(self,paciente,medico,fecha,documento):
        return self.citaManagerInstance._delete_cita(paciente, medico, fecha, documento)

    def  obtener_citas_paciente_service(self,documento):
        return self.citaManagerInstance._obtener_citas_paciente(documento)
