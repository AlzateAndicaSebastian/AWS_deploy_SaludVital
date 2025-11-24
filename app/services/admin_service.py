from app.managers.admin_manager import AdminManager
from app.config import crear_token_acceso
import os


class AdminService:
    # Leyenda: Modo simplificado de administración.
    # Un único usuario admin definido por variables de entorno:
    # ADMIN_USERNAME y ADMIN_SECRET_KEY (password). No existe registro vía API.
    # Ventaja: reduce superficie de ataque; la rotación de credenciales se hace fuera del sistema.
    def __init__(self):
        self.admin_manager = AdminManager()  # Se mantiene para gestión de exámenes legacy.
        self._admin_username = os.getenv("ADMIN_USERNAME", "admin")
        self._admin_secret = os.getenv("ADMIN_SECRET_KEY", "clave_admin_secreta_por_defecto")

    def login_admin(self, username: str, password: str) -> dict:
        """
        Autentica a un administrador y genera un token de acceso.
        """
        if username == self._admin_username and password == self._admin_secret:
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