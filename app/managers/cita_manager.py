import json
import os
import secrets
import string
from datetime import datetime
from filelock import FileLock


class CitaManager:

    def __init__(self, base_path=None):
        """
        En vez de un solo archivo global, ahora trabajamos con una carpeta donde
        cada paciente tendrá su propio archivo JSON.
        """
        if base_path is None:
            # Persistencia fuera del proyecto (como en EC2)
            base_path = os.path.expanduser("~/memoryApps/saludVital/citas/")

        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    # ===============================================================
    #  📌 UTILIDADES DE ARCHIVOS POR PACIENTE
    # ===============================================================

    def _get_file_path(self, documento):
        """
        Retorna la ruta del archivo JSON del paciente.
        """
        return os.path.join(self.base_path, f"{documento}.json")

    def _load_data_paciente(self, documento):
        """
        Carga las citas específicas del paciente.
        """
        file_path = self._get_file_path(documento)
        lock_path = file_path + ".lock"

        if not os.path.exists(file_path):
            return []

        with FileLock(lock_path):
            try:
                with open(file_path, "r") as f:
                    return json.load(f)
            except Exception:
                return []

    def _save_data_paciente(self, documento, citas):
        """
        Guarda únicamente las citas del paciente.
        """
        file_path = self._get_file_path(documento)
        lock_path = file_path + ".lock"

        with FileLock(lock_path):
            with open(file_path, "w") as f:
                json.dump(citas, f, indent=4)

    # ===============================================================
    #  📌  OPERACIONES PRINCIPALES
    # ===============================================================

    def agendar_cita(self, paciente, medico, fecha, documento, tipoCita, motivoPaciente):
        """
        Guarda la cita en el archivo individual del paciente.
        """

        citas_paciente = self._load_data_paciente(documento)

        # Validar fecha
        fecha_valida = self._verificar_fecha(fecha)

        # (Opcional) Validación si quieres evitar duplicados exactos:
        # if self._cita_existente(citas_paciente, medico, fecha_valida):
        #     raise ValueError("Cita duplicada.")

        nueva_cita = {
            "paciente": paciente,
            "medico": medico,
            "fecha": fecha_valida,
            "documento": documento,
            "registrado": datetime.now().isoformat(),
            "codigo_cita": self._generar_codigo_cita(),
            "tipoCita": tipoCita,
            "motivoPaciente": motivoPaciente,
            "prioridad": self._calcular_prioridad(tipoCita)
        }

        citas_paciente.append(nueva_cita)

        self._save_data_paciente(documento, citas_paciente)
        return nueva_cita

    def _cita_existente(self, citas_paciente, medico, fecha):
        """
        Busca si el paciente ya tiene una cita con ese médico en esa fecha.
        """
        return any(c["medico"] == medico and c["fecha"] == fecha for c in citas_paciente)

    # ===============================================================
    #  📌 CONSULTAS Y ELIMINACIONES POR PACIENTE
    # ===============================================================

    def obtener_citas_paciente(self, documento):
        """
        Retorna todas las citas de un paciente.
        """
        return self._load_data_paciente(documento)

    def eliminar_cita(self, paciente, medico, fecha, documento):
        """
        Elimina una cita del archivo específico del paciente.
        """
        citas = self._load_data_paciente(documento)
        inicial = len(citas)

        citas = [
            c for c in citas
            if not (c["paciente"] == paciente and
                    c["medico"] == medico and
                    c["fecha"] == fecha and
                    c["documento"] == documento)
        ]

        if len(citas) < inicial:
            self._save_data_paciente(documento, citas)
            return True

        return False

    # ===============================================================
    #  📌 UTILIDADES DE LOGICA
    # ===============================================================

    def _generar_codigo_cita(self, length=6):
        chars = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(chars) for _ in range(length))

    def _calcular_prioridad(self, tipoCita):
        prioridades = {
            "Emergencia": 1,
            "Urgencia": 2,
            "Consulta": 3,
            "Control": 4,
            "Reevaluacion": 5,
            "Revaloracion": 6,
            "Revision": 7,
            "Examen": 8,
            "Otro": 9,
        }
        return prioridades.get(tipoCita, -1)

    def _verificar_fecha(self, fecha):
        try:
            fecha_cita = datetime.fromisoformat(fecha)
        except ValueError:
            raise ValueError("Formato de fecha inválido. Use ISO 8601.")

        if fecha_cita < datetime.now():
            raise ValueError("No se puede agendar una cita en una fecha pasada.")

        return fecha
