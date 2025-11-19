import json
import os.path
import os
import secrets
import string
from datetime import datetime

class CitaManager:
    def __init__(self, file_path="citas.json"):
        # si no se encuentra el directorio de persistencia, se crea uno en el home del user
        if file_path is None:
            file_path = os.path.expanduser("~/citas.json")
        # se asegura que el directorio exista para la persistencia
        self.file_path = file_path
        self.citas = self._load_data()

    def agendar_cita(self, paciente, medico, fecha):
        if self._cita_existente(paciente, medico, fecha):
            raise ValueError("Cita duplicada.")
        self.citas.append({
            "paciente": paciente,
            "medico": medico,
            "fecha": fecha,
            "registrado": datetime.now().isoformat()
        })


    def _cita_existente(self, paciente, medico, fecha):
        return any(cita for cita in self.citas if cita["paciente"] == paciente and cita["fecha"] == fecha)

    def _load_data(self):
        if not os.path.exists(self.file_path):
            return []
        with open (self.file_path, "r") as f:
            return json.load(f)

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

















