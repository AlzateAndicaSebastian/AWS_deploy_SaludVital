import json
import hashlib
import os
from datetime import datetime
from pathlib import Path
from filelock import FileLock
from app.config import BASE_DATA_DIR
from app.utils.file_atomic import locked_atomic_write, locked_atomic_load


class MedicoManager:
    # Leyenda: Fachada legacy para operaciones de médicos.
    # Responsabilidades actuales:
    # - Registro / autenticación de médicos (persistencia en archivos individuales)
    # - Gestión de agenda (archivo por médico con lista de citas)
    # - Almacenamiento de diagnóstico por código de cita (1 archivo por diagnóstico)
    # Relación con servicios: MedicoService delega aquí mientras se migra a repositorios.
    # Futuro: separar en repositorios y services (MedicoRepository, AgendaService, DiagnosticoService).
    def __init__(self, base_dir=None):
        """
        Gestiona el registro y autenticación de médicos.
        base_dir permite aislar el almacenamiento (útil en tests).
        """
        self.base_dir = base_dir or BASE_DATA_DIR
        self.medicos_dir = self.base_dir / "medicos"
        self.medicos_dir.mkdir(parents=True, exist_ok=True)
        
        # Directorio para almacenar las agendas de los médicos
        self.agendas_dir = self.base_dir / "agendas"
        self.agendas_dir.mkdir(parents=True, exist_ok=True)
        
        # Directorio para almacenar los diagnósticos
        self.diagnosticos_dir = self.base_dir / "diagnosticos"
        self.diagnosticos_dir.mkdir(parents=True, exist_ok=True)

    def _hash_contraseña(self, contraseña: str) -> str:
        """
        Genera un hash de la contraseña para almacenarla de forma segura.
        """
        return hashlib.sha256(contraseña.encode()).hexdigest()

    def _guardar_medico(self, datos_medico: dict):
        """
        Guarda los datos del médico en un archivo JSON.
        """
        archivo = self.medicos_dir / f"{datos_medico['documento']}.json"
        # No almacenamos la contraseña en texto plano
        datos_a_guardar = datos_medico.copy()
        datos_a_guardar["contraseña"] = self._hash_contraseña(datos_medico["contraseña"])
        datos_a_guardar["fecha_registro"] = datetime.now().isoformat()
        locked_atomic_write(str(archivo), datos_a_guardar)

    def _cargar_medico(self, documento: str) -> dict:
        """
        Carga los datos de un médico desde su archivo JSON.
        """
        archivo = self.medicos_dir / f"{documento}.json"
        if not os.path.exists(archivo):
            return None
        return locked_atomic_load(str(archivo))

    def registrar_medico(self, documento: str, nombre_completo: str, contraseña: str,
                         telefono: str, email: str, especialidad: str) -> bool:
        """
        Registra un nuevo médico en el sistema.
        """
        # Verificar si el médico ya existe
        if self._cargar_medico(documento):
            raise ValueError("Ya existe un médico con ese documento")

        # Crear diccionario con los datos del médico
        datos_medico = {
            "documento": documento,
            "nombre_completo": nombre_completo,
            "contraseña": contraseña,
            "telefono": telefono,
            "email": email,
            "especialidad": especialidad,
            "citas_atendidas": []  # Lista de códigos de citas atendidas
        }

        # Guardar médico
        self._guardar_medico(datos_medico)
        return True

    def autenticar_medico(self, documento: str, contraseña: str) -> bool:
        """
        Autentica a un médico verificando su documento y contraseña.
        """
        medico = self._cargar_medico(documento)
        if not medico:
            return False

        hash_contraseña = self._hash_contraseña(contraseña)
        return medico.get("contraseña") == hash_contraseña

    def obtener_datos_medico(self, documento: str) -> dict:
        """
        Obtiene los datos de un médico sin la contraseña.
        """
        medico = self._cargar_medico(documento)
        if medico:
            # Remover la contraseña antes de devolver los datos
            medico.pop("contraseña", None)
            return medico
        return None

    def existe_medico(self, documento: str) -> bool:
        """
        Verifica si un médico está registrado en el sistema.
        """
        archivo = self.medicos_dir / f"{documento}.json"
        return os.path.exists(archivo)

    def obtener_agenda_medico(self, documento: str) -> list:
        """
        Obtiene todas las citas asignadas a un médico.
        """
        archivo = self.agendas_dir / f"{documento}.json"
        lock_path = str(archivo) + ".lock"
        
        if not os.path.exists(archivo):
            return []

        with FileLock(lock_path):
            try:
                with open(archivo, "r") as f:
                    return json.load(f)
            except Exception:
                return []

    def actualizar_agenda_medico(self, documento: str, citas: list):
        """
        Actualiza la agenda de un médico.
        """
        archivo = self.agendas_dir / f"{documento}.json"
        lock_path = str(archivo) + ".lock"
        
        with FileLock(lock_path):
            tmp_path = str(archivo) + ".tmp"
            with open(tmp_path, "w") as f:
                json.dump(citas, f, indent=4)
            os.replace(tmp_path, archivo)

    def agregar_diagnostico(self, codigo_cita: str, diagnostico_data: dict):
        # Leyenda: Persistencia simple de diagnóstico por cita.
        # Se planea migrar a DiagnosticoRepository que agrupará todos en un sólo archivo.
        archivo = self.diagnosticos_dir / f"{codigo_cita}.json"
        # Normalizar datetimes en el dict si presentes
        for k, v in list(diagnostico_data.items()):
            if hasattr(v, "isoformat"):
                try:
                    diagnostico_data[k] = v.isoformat()
                except Exception:
                    pass
        diagnostico_data["fecha_registro"] = datetime.now().isoformat()
        locked_atomic_write(str(archivo), diagnostico_data)

    def obtener_diagnostico(self, codigo_cita: str) -> dict:
        """
        Obtiene el diagnóstico de una cita específica.
        """
        archivo = self.diagnosticos_dir / f"{codigo_cita}.json"
        
        if not os.path.exists(archivo):
            return None
        return locked_atomic_load(str(archivo))

    def marcar_cita_atendida(self, documento_medico: str, codigo_cita: str):
        """
        Marca una cita como atendida por un médico.
        """
        medico = self._cargar_medico(documento_medico)
        if medico:
            if "citas_atendidas" not in medico:
                medico["citas_atendidas"] = []
            
            if codigo_cita not in medico["citas_atendidas"]:
                medico["citas_atendidas"].append(codigo_cita)
                
                # Guardar cambios
                archivo = self.medicos_dir / f"{documento_medico}.json"
                locked_atomic_write(str(archivo), medico)
