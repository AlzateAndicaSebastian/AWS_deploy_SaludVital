import json
import os.path
import os
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
        return True

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