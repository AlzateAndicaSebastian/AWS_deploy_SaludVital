from pathlib import Path
import jwt
import os
from datetime import datetime, timedelta

BASE_DATA_DIR = Path("~/memoryApps/saludVital/").expanduser()
BASE_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Clave secreta para JWT (debería estar en variables de entorno en producción)
SECRET_KEY = os.getenv("SECRET_KEY", "clave_secreta_por_defecto")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def crear_token_acceso(data: dict):
    """
    Crea un token de acceso JWT con los datos proporcionados.
    Incluye el documento del paciente en el token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decodificar_token_acceso(token: str):
    """
    Decodifica un token de acceso JWT y devuelve los datos.
    """
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload

def verificar_documento_paciente(documento: str):
    """
    Verifica si el documento del paciente está registrado.
    Esta es una implementación básica que verifica si existe
    un archivo JSON para el paciente.
    """
    paciente_file_path = BASE_DATA_DIR / "pacientes" / f"{documento}.json"
    return paciente_file_path.exists()

def obtener_directorio_pacientes():
    """
    Obtiene el directorio donde se almacenan los datos de los pacientes.
    """
    pacientes_dir = BASE_DATA_DIR / "pacientes"
    pacientes_dir.mkdir(parents=True, exist_ok=True)
    return pacientes_dir

def obtener_archivo_paciente(documento: str):
    """
    Obtiene la ruta del archivo JSON de un paciente específico.
    """
    return obtener_directorio_pacientes() / f"{documento}.json"