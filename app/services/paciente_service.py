from app.managers.paciente_manager import PacienteManager
from app.config import crear_token_acceso


class PacienteService:
    def __init__(self):
        self.paciente_manager = PacienteManager()

    def registrar_paciente(self, documento: str, nombre_completo: str, contraseña: str,
                          telefono: str, email: str, edad: int, sexo: str) -> bool:
        """
        Registra un nuevo paciente en el sistema.
        """
        try:
            return self.paciente_manager.registrar_paciente(
                documento, nombre_completo, contraseña, telefono, email, edad, sexo
            )
        except ValueError as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al registrar paciente: {str(e)}")

    def login_paciente(self, documento: str, contraseña: str) -> dict:
        """
        Autentica a un paciente y genera un token de acceso.
        """
        if self.paciente_manager.autenticar_paciente(documento, contraseña):
            # Obtener datos del paciente sin la contraseña
            datos_paciente = self.paciente_manager.obtener_datos_paciente(documento)
            if datos_paciente:
                # Crear token de acceso con los datos del paciente
                token = crear_token_acceso({
                    "documento": documento,
                    "nombre_completo": datos_paciente["nombre_completo"]
                })
                
                return {
                    "token": token,
                    "paciente": datos_paciente
                }
        
        raise ValueError("Credenciales inválidas")

    def verificar_paciente(self, documento: str) -> bool:
        """
        Verifica si un paciente está registrado en el sistema.
        """
        return self.paciente_manager.existe_paciente(documento)