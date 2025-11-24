import json
import hashlib
import os
from datetime import datetime
from app.config import obtener_archivo_paciente

class PacienteManager:
    def __init__(self, base_dir=None):
        """
        Gestiona el registro y autenticación de pacientes.
        base_dir permite aislar el almacenamiento (útil en tests).
        """
        from app.config import BASE_DATA_DIR
        self.base_dir = base_dir or BASE_DATA_DIR
        # Directorio local de pacientes según base_dir
        self._pacientes_dir = os.path.join(self.base_dir, 'pacientes')
        os.makedirs(self._pacientes_dir, exist_ok=True)

    def _archivo_paciente(self, documento: str) -> str:
        return os.path.join(self._pacientes_dir, f"{documento}.json")

    def _hash_contraseña(self, contraseña: str) -> str:
        """
        Genera un hash de la contraseña para almacenarla de forma segura.
        """
        return hashlib.sha256(contraseña.encode()).hexdigest()

    def _guardar_paciente(self, datos_paciente: dict):
        """
        Guarda los datos del paciente en un archivo JSON usando base_dir.
        """
        archivo = self._archivo_paciente(datos_paciente["documento"])
        datos_a_guardar = datos_paciente.copy()
        datos_a_guardar["contraseña"] = self._hash_contraseña(datos_paciente["contraseña"])
        datos_a_guardar["fecha_registro"] = datetime.now().isoformat()
        with open(archivo, "w") as f:
            json.dump(datos_a_guardar, f, indent=4)

    def _cargar_paciente(self, documento: str) -> dict:
        archivo = self._archivo_paciente(documento)
        if not os.path.exists(archivo):
            return None
        with open(archivo, "r") as f:
            return json.load(f)

    def registrar_paciente(self, documento: str, nombre_completo: str, contraseña: str, 
                          telefono: str, email: str, edad: int, sexo: str) -> bool:
        """
        Registra un nuevo paciente en el sistema.
        Respeta base_dir para aislamiento en tests.
        """
        if self._cargar_paciente(documento):
            raise ValueError("Ya existe un paciente con ese documento")
        datos_paciente = {
            "documento": documento,
            "nombre_completo": nombre_completo,
            "contraseña": contraseña,
            "telefono": telefono,
            "email": email,
            "edad": self.verificar_edad(edad),
            "sexo": sexo
        }
        self._guardar_paciente(datos_paciente)
        return True

    def verificar_edad(self, edad):
        try:
            edad_int = int(edad)
        except (TypeError, ValueError):
            raise ValueError("Edad inválida")
        if edad_int < 18:
            raise ValueError("Debe ser mayor de edad para registrarse")
        return edad_int

    def autenticar_paciente(self, documento: str, contraseña: str) -> bool:
        paciente = self._cargar_paciente(documento)
        if not paciente:
            return False
        hash_contraseña = self._hash_contraseña(contraseña)
        return paciente.get("contraseña") == hash_contraseña

    def obtener_datos_paciente(self, documento: str) -> dict:
        paciente = self._cargar_paciente(documento)
        if paciente:
            paciente.pop("contraseña", None)
            return paciente
        return None

    def existe_paciente(self, documento: str) -> bool:
        return os.path.exists(self._archivo_paciente(documento))
