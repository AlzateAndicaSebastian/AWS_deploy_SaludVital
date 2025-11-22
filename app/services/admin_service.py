from app.managers.admin_manager import AdminManager
from app.config import crear_token_acceso
import os


class AdminService:
    def __init__(self):
        self.admin_manager = AdminManager()

    def login_admin(self, username: str, password: str) -> dict:
        """
        Autentica a un administrador y genera un token de acceso.
        """
        # Clave secreta para administradores (debería estar en variables de entorno)
        ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY", "clave_admin_secreta_por_defecto")
        
        # En una implementación real, se debería usar un sistema de autenticación más seguro
        # Esta es una implementación básica para demostración
        if username == "admin" and password == ADMIN_SECRET_KEY:
            # Crear token de acceso con los datos del administrador
            token = crear_token_acceso({
                "username": username,
                "tipo_usuario": "admin"
            })
            
            return {
                "token": token,
                "mensaje": "Autenticación exitosa"
            }
        
        raise ValueError("Credenciales inválidas")

    def crear_resultado_examen(self, codigo_examen: str, datos_examen: dict):
        """
        Crea un resultado de examen.
        """
        self.admin_manager.crear_resultado_examen(codigo_examen, datos_examen)

    def obtener_resultado_examen(self, codigo_examen: str) -> dict:
        """
        Obtiene el resultado de un examen específico.
        """
        return self.admin_manager.obtener_resultado_examen(codigo_examen)

    def listar_examenes_paciente(self, documento_paciente: str) -> list:
        """
        Lista todos los exámenes de un paciente específico.
        """
        return self.admin_manager.listar_examenes_paciente(documento_paciente)

    def actualizar_estado_examen(self, codigo_examen: str, estado: str, 
                               observaciones: str = None) -> bool:
        """
        Actualiza el estado de un examen.
        """
        return self.admin_manager.actualizar_estado_examen(codigo_examen, estado, observaciones)