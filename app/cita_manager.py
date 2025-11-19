import json
import os.path
import os
import secrets
import string
from datetime import datetime

# Por regla de negocio las citas seran asignadas por una secretaria como lo demanda este CRUD
# agendando las citas si el paciente se presenta personalmente, de el mismo modo
# las citas solo podran ser canceladas si el cliente va fisicamente y pide cancelarla (eliminar la cita)

class CitaManager:
    def __init__(self, file_path="citas.json"):
        # si no se encuentra el directorio de persistencia, se crea uno en el home del user
        if file_path is None:
            file_path = os.path.expanduser("~/citas.json")
        # se asegura que el directorio exista para la persistencia
        self.file_path = file_path
        self.citas = self._load_data()

    def agendar_cita(self, paciente, medico, fecha, documento, tipoCita, motivoPaciente):
        # if self._cita_existente(paciente, medico, fecha):
        #     raise ValueError("Cita duplicada.")  para esta logica se permiten varias citas en la misma fecha
        self.citas.append({
            "paciente": paciente,
            "medico": medico, # los nombres de los medicos tambien estan asignados en el navbar del front
            "fecha": fecha,
            "documento": documento,
            "registrado": datetime.now().isoformat(), # fecha de registro
            "codigo_cita": self._generar_codigo_cita(), # codigo de cita unico
            "tipoCita": tipoCita,
            "motivoPaciente": motivoPaciente, # breve descripcion del paciente de su motivo de consulta
            "prioridad": self._calcular_prioridad(tipoCita)
        })
        self._save_data() # persistencia en el archivo


    def _cita_existente(self, paciente, medico, fecha):
        return any(cita for cita in self.citas if cita["paciente"] == paciente and cita["fecha"] == fecha)

    def _load_data(self):
        if not os.path.exists(self.file_path):
            return []
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except Exception:
            return []

    def _save_data(self):
        with open (self.file_path, "w") as f :
            json.dump(self.citas,f,indent=4)

    def _delete_cita(self, paciente, medico, fecha ,documento):
        citas_actuales = len(self.citas)
        self.citas = [
            cita for cita in self.citas
            if not (
                cita["paciente"] == paciente and
                cita["medico"] == medico and
                cita["fecha"] == fecha and
                cita["documento"] == documento
            )
        ]
        if len(self.citas) < citas_actuales: # verificamos haber eliminado la cita (reducir el json)
            self._save_data()  # guardamos la actualizacion
            return  True  # si la eliminamos retorna true
        return False # si no se encontro la cita a eliminar retorna false

    def _generar_codigo_cita(self, length=6):
        chars = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(chars) for _ in range(length))

    def _calcular_prioridad(self, tipoCita): # para evitar errores estos tipos deben estar pre-escritos en el html en un navbar
        if tipoCita == "Emergencia":
            return 1
        elif tipoCita == "Urgencia":
            return 2
        elif tipoCita == "Consulta":
            return 3
        elif tipoCita == "Control":
            return 4
        elif tipoCita == "Reevaluacion":
            return 5
        elif tipoCita == "Revaloracion":
            return 6
        elif tipoCita == "Revision":
            return 7
        elif tipoCita == "Examen":
            return 8
        else:
            return -1 # prioridad desconocida o erronea

    def _obtener_citas_paciente(self,documento):
        return [cita for cita in self.citas if cita["documento"] == documento]
















