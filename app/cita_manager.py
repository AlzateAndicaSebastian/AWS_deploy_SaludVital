import json
import os.path
import os
import secrets
import string
from datetime import datetime
from filelock import FileLock

# Inicialización y persistencia: Al crear la instancia, se asegura que el archivo de persistencia exista
# y carga las citas desde el archivo.
# Agendamiento de citas: Permite agendar nuevas citas, generando un código único, asignando prioridad
# según el tipo de cita y validando que la fecha no sea pasada.
# Eliminación y consulta: Permite eliminar citas específicas y consultar las citas
# de un paciente por su documento.
# Validaciones: Verifica el formato y validez de la fecha, y calcula la prioridad de la cita
# según reglas de negocio predefinidas.
# Concurrencia: Usa la librería filelock para asegurar que solo un proceso acceda al archivo de citas a la vez,
# tanto en lectura como en escritura.
# Esto previene corrupción de datos y garantiza que las solicitudes concurrentes
# se atiendan en orden, respetando la prioridad y el orden de llegada

class CitaManager:
    def __init__(self, file_path="citas.json"):
        # si no se encuentra el directorio de persistencia, se crea uno en el home del user
        if file_path is None:
            file_path = os.path.expanduser("~/memoryApps/saludVital/citas.json")
        # se asegura que el directorio exista para la persistencia
        self.file_path = file_path
        self.citas = self._load_data()

    def agendar_cita(self, paciente, medico, fecha, documento, tipoCita, motivoPaciente):
        # if self._cita_existente(paciente, medico, fecha):
        #     raise ValueError("Cita duplicada.")  para esta logica se permiten varias citas en la misma fecha
        self.citas.append({
            "paciente": paciente,
            "medico": medico, # los nombres de los medicos tambien estan asignados en el navbar del front (aparecen los disponibles)
            "fecha": self._verificar_fecha(fecha), # fecha disponible para la cita -- usar un calendario sencillo en html
            "documento": documento,
            "registrado": datetime.now().isoformat(), # fecha y hora de registro de la cita
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
        lock_path = self.file_path + ".lock"
        with FileLock(lock_path):
            try:
                with open(self.file_path, "r") as f:
                    return json.load(f)
            except Exception:
                return []

def _save_data(self):
    lock_path = self.file_path + ".lock"
    with FileLock(lock_path):
        with open(self.file_path, "w") as f:
            json.dump(self.citas, f, indent=4)

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
        elif tipoCita == "Otro":
            return 9
        else:
            return -1 # prioridad desconocida o erronea

    def _obtener_citas_paciente(self,documento):
        return [cita for cita in self.citas if cita["documento"] == documento]

    def _verificar_fecha(self, fecha):
        # Se asume que 'fecha' es un string en formato ISO (YYYY-MM-DD o YYYY-MM-DDTHH:MM)
        try:
            fecha_cita = datetime.fromisoformat(fecha)
        except ValueError:
            raise ValueError("Formato de fecha inválido. Use ISO 8601 (YYYY-MM-DD o YYYY-MM-DDTHH:MM).")
        if fecha_cita < datetime.now():
            raise ValueError("No se puede agendar una cita en una fecha pasada.")
        return fecha
















