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


    def _hash_contraseña(self, contraseña: str) -> str:
        """
        Genera un hash de la contraseña para almacenarla de forma segura.
        """
        return hashlib.sha256(contraseña.encode()).hexdigest()

    def _guardar_paciente(self, datos_paciente: dict):
        """
        Guarda los datos del paciente en un archivo JSON.
        """
        archivo = obtener_archivo_paciente(datos_paciente["documento"])
        # No almacenamos la contraseña en texto plano
        datos_a_guardar = datos_paciente.copy()
        datos_a_guardar["contraseña"] = self._hash_contraseña(datos_paciente["contraseña"])
        datos_a_guardar["fecha_registro"] = datetime.now().isoformat()
        
        with open(archivo, "w") as f:
            json.dump(datos_a_guardar, f, indent=4)

    def _cargar_paciente(self, documento: str) -> dict:
        """
        Carga los datos de un paciente desde su archivo JSON.
        """
        archivo = obtener_archivo_paciente(documento)
        if not os.path.exists(archivo):
            return None

        with open(archivo, "r") as f:
            return json.load(f)

    def registrar_paciente(self, documento: str, nombre_completo: str, contraseña: str, 
                          telefono: str, email: str, edad: int, sexo: str) -> bool:
        """
        Registra un nuevo paciente en el sistema.
        """
        # Verificar si el paciente ya existe
        if self._cargar_paciente(documento):
            raise ValueError("Ya existe un paciente con ese documento")

        # Crear diccionario con los datos del paciente
        datos_paciente = {
            "documento": documento,
            "nombre_completo": nombre_completo,
            "contraseña": contraseña,
            "telefono": telefono,
            "email": email,
            "edad": self.verificar_edad(edad),
            "sexo": sexo
        }

        # Guardar paciente
        self._guardar_paciente(datos_paciente)
        return True

    def verificar_edad(self, edad):
        # verificamos que sea mayor de 18 años
        try:
            edad_int = int(edad)
        except (TypeError, ValueError):
            raise ValueError("Edad inválida")
        if edad_int < 18:
            raise ValueError("Debe ser mayor de edad para registrarse")
        return edad_int

    def autenticar_paciente(self, documento: str, contraseña: str) -> bool:
        """
        Autentica a un paciente verificando su documento y contraseña.
        """
        paciente = self._cargar_paciente(documento)
        if not paciente:
            return False

        hash_contraseña = self._hash_contraseña(contraseña)
        return paciente.get("contraseña") == hash_contraseña

    def obtener_datos_paciente(self, documento: str) -> dict:
        """
        Obtiene los datos de un paciente sin la contraseña.
        """
        paciente = self._cargar_paciente(documento)
        if paciente:
            # Remover la contraseña antes de devolver los datos
            paciente.pop("contraseña", None)
            return paciente
        return None

    def existe_paciente(self, documento: str) -> bool:
        """
        Verifica si un paciente está registrado en el sistema.
        """
        return os.path.exists(obtener_archivo_paciente(documento))