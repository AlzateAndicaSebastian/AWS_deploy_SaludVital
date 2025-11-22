from app.managers.medico_manager import MedicoManager
from app.config import crear_token_acceso
from app.managers.cita_manager import CitaManager
from app.managers.admin_manager import AdminManager
import os
from datetime import datetime
import secrets
import string


class MedicoService:
    def __init__(self):
        self.medico_manager = MedicoManager()
        self.cita_manager = CitaManager()
        self.admin_manager = AdminManager()

    def registrar_medico(self, documento: str, nombre_completo: str, contraseña: str,
                         telefono: str, email: str, especialidad: str) -> bool:
        """
        Registra un nuevo médico en el sistema.
        """
        try:
            return self.medico_manager.registrar_medico(
                documento, nombre_completo, contraseña, telefono, email, especialidad
            )
        except ValueError as e:
            raise e
        except Exception as e:
            raise Exception(f"Error al registrar médico: {str(e)}")

    def login_medico(self, documento: str, contraseña: str) -> dict:
        """
        Autentica a un médico y genera un token de acceso.
        """
        if self.medico_manager.autenticar_medico(documento, contraseña):
            # Obtener datos del médico sin la contraseña
            datos_medico = self.medico_manager.obtener_datos_medico(documento)
            if datos_medico:
                # Crear token de acceso con los datos del médico
                token = crear_token_acceso({
                    "documento": documento,
                    "nombre_completo": datos_medico["nombre_completo"],
                    "tipo_usuario": "medico"
                })
                
                return {
                    "token": token,
                    "medico": datos_medico
                }
        
        raise ValueError("Credenciales inválidas")

    def verificar_medico(self, documento: str) -> bool:
        """
        Verifica si un médico está registrado en el sistema.
        """
        return self.medico_manager.existe_medico(documento)

    def obtener_agenda_medico(self, documento: str) -> list:
        """
        Obtiene la agenda de un médico con sus citas futuras.
        """
        # Obtener todas las citas del médico
        agenda_completa = self.medico_manager.obtener_agenda_medico(documento)
        
        # Filtrar solo citas futuras
        ahora = datetime.now()
        agenda_futura = []
        
        for cita in agenda_completa:
            try:
                fecha_cita = datetime.fromisoformat(cita["fecha"])
                if fecha_cita >= ahora:
                    agenda_futura.append(cita)
            except ValueError:
                # Si hay un error en el formato de fecha, incluir la cita para revisión
                agenda_futura.append(cita)
        
        return agenda_completa

    def cerrar_cita(self, documento_medico: str, codigo_cita: str, estado: str, 
                    diagnostico: dict = None) -> bool:
        """
        Cierra una cita con un estado específico. Si el estado es 'realizada',
        se puede incluir un diagnóstico.
        """
        if estado not in ['realizada', 'cancelada', 'noAsistida']:
            raise ValueError("Estado de cita inválido")
            
        # Obtener la agenda del médico
        agenda = self.medico_manager.obtener_agenda_medico(documento_medico)
        
        # Buscar la cita específica
        cita_encontrada = None
        for i, cita in enumerate(agenda):
            if cita.get("codigo_cita") == codigo_cita:
                cita_encontrada = cita
                indice_cita = i
                break
                
        if not cita_encontrada:
            raise ValueError("Cita no encontrada en la agenda del médico")
            
        # Actualizar el estado de la cita
        cita_encontrada["estado"] = estado
        
        # Si la cita se marca como realizada, procesar el diagnóstico
        if estado == "realizada" and diagnostico:
            # Agregar información del médico al diagnóstico
            datos_medico = self.medico_manager.obtener_datos_medico(documento_medico)
            diagnostico["medico"] = {
                "documento": documento_medico,
                "nombre": datos_medico["nombre_completo"],
                "especialidad": datos_medico["especialidad"]
            }
            
            # Guardar el diagnóstico
            self.medico_manager.agregar_diagnostico(codigo_cita, diagnostico)
            
            # Marcar cita como atendida por el médico
            self.medico_manager.marcar_cita_atendida(documento_medico, codigo_cita)
            
            # Si se solicitaron exámenes, crear registros de exámenes
            if "examenes_solicitados" in diagnostico:
                for examen in diagnostico["examenes_solicitados"]:
                    # Generar código único para el examen
                    codigo_examen = self._generar_codigo_examen()
                    
                    # Crear registro de examen
                    datos_examen = {
                        "documento_paciente": cita_encontrada.get("documento"),
                        "paciente": cita_encontrada.get("paciente"),
                        "codigo_cita": codigo_cita,
                        "examen_solicitado": examen,
                        "medico": diagnostico["medico"],
                        "diagnostico": diagnostico.get("descripcion", ""),
                        "estado": "pendiente"
                    }
                    
                    # Guardar el examen usando el admin manager
                    self.admin_manager.crear_resultado_examen(codigo_examen, datos_examen)
        
        # Actualizar la agenda
        agenda[indice_cita] = cita_encontrada
        self.medico_manager.actualizar_agenda_medico(documento_medico, agenda)
        
        return True

    def _generar_codigo_examen(self, length=8):
        """
        Genera un código único para un examen.
        """
        chars = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(chars) for _ in range(length))

    def obtener_diagnostico(self, codigo_cita: str) -> dict:
        """
        Obtiene el diagnóstico de una cita específica.
        """
        return self.medico_manager.obtener_diagnostico(codigo_cita)