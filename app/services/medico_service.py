from app.managers.medico_manager import MedicoManager
from app.config import crear_token_acceso
from app.managers.cita_manager import CitaManager
from app.managers.admin_manager import AdminManager
from app.services.examen_workflow_service import ExamenWorkflowService
from app.metrics.metrics import inc_medico_registrado, inc_medico_login, inc_examen_solicitado
import os
from datetime import datetime, timezone
import secrets
import string


class MedicoService:
    # Leyenda: Servicio de médicos.
    # Responsabilidades: registro/login, agenda, cierre de cita y generación de solicitudes de examen.
    # Migración: sustituye creación directa de archivos de exámenes por ExamenWorkflowService.
    def __init__(self):
        # ...existing code...
        self.medico_manager = MedicoManager()
        self.cita_manager = CitaManager()
        self.admin_manager = AdminManager()  # Legacy para resultados directos (se irá deprecando)
        self.examen_workflow = ExamenWorkflowService()  # Nuevo workflow unificado

    def registrar_medico(self, documento: str, nombre_completo: str, contraseña: str,
                         telefono: str, email: str, especialidad: str) -> bool:
        """
        Registra un nuevo médico en el sistema.
        """
        try:
            registro = self.medico_manager.registrar_medico(
                documento, nombre_completo, contraseña, telefono, email, especialidad
            )
            if registro:
                inc_medico_registrado()
            return registro
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
                inc_medico_login()
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
        Leyenda (refactor): Se normaliza la fecha de cada cita para evitar el error
        'can't compare offset-naive and offset-aware datetimes'. Se aceptan formatos:
        - 2025-11-24T12:00:00 (naive)
        - 2025-11-24T12:00:00Z (UTC)
        - 2025-11-24T12:00:00+00:00 (offset)
        Retorna solo citas con fecha >= ahora.
        """
        agenda_completa = self.medico_manager.obtener_agenda_medico(documento)
        ahora_local = datetime.now()  # para comparar con fechas naive
        ahora_utc = datetime.now(timezone.utc)  # para comparar con fechas aware
        futuras = []
        for cita in agenda_completa:
            raw = cita.get("fecha")
            if not isinstance(raw, str):
                futuras.append(cita)
                continue
            iso = raw.strip()
            if iso.endswith("Z"):
                iso = iso[:-1] + "+00:00"  # compatibilidad con fromisoformat
            try:
                fecha_cita = datetime.fromisoformat(iso)
                if fecha_cita.tzinfo is None:
                    # naive vs naive
                    if fecha_cita >= ahora_local:
                        futuras.append(cita)
                else:
                    # aware -> convertir a UTC y comparar
                    if fecha_cita.astimezone(timezone.utc) >= ahora_utc:
                        futuras.append(cita)
            except Exception:
                # Si hay un problema de parsing, incluir para revisión manual
                futuras.append(cita)
        return futuras

    def cerrar_cita(self, documento_medico: str, codigo_cita: str, estado: str, 
                    diagnostico: dict = None) -> bool:
        """
        Cierra una cita con un estado específico. Si el estado es 'realizada',
        se puede incluir un diagnóstico.
        """
        if estado not in ['realizada', 'cancelada', 'noAsistida']:
            raise ValueError("Estado de cita inválido")
        agenda = self.medico_manager.obtener_agenda_medico(documento_medico)
        cita_encontrada = None
        for i, cita in enumerate(agenda):
            if cita.get("codigo_cita") == codigo_cita:
                cita_encontrada = cita
                indice_cita = i
                break
        if not cita_encontrada:
            raise ValueError("Cita no encontrada en la agenda del médico")
        cita_encontrada["estado"] = estado
        if estado == "realizada" and diagnostico:
            datos_medico = self.medico_manager.obtener_datos_medico(documento_medico)
            diagnostico["medico"] = {
                "documento": documento_medico,
                "nombre": datos_medico["nombre_completo"],
                "especialidad": datos_medico["especialidad"]
            }
            self.medico_manager.agregar_diagnostico(codigo_cita, diagnostico)
            self.medico_manager.marcar_cita_atendida(documento_medico, codigo_cita)
            if "examenes_solicitados" in diagnostico:
                for examen in diagnostico["examenes_solicitados"]:
                    # Leyenda: En vez de crear resultado directo, generamos solicitud formal.
                    created = self.examen_workflow.crear_solicitud(
                        codigo_cita=codigo_cita,
                        documento_paciente=cita_encontrada.get("documento"),
                        documento_medico=documento_medico,
                        tipo_examen=examen
                    )
                    if created:
                        inc_examen_solicitado()
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