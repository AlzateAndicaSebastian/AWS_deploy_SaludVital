from app.managers.paciente_manager import PacienteManager
from app.config import crear_token_acceso
from app.managers.admin_manager import AdminManager
from app.services.examen_workflow_service import ExamenWorkflowService


class PacienteService:
    # Leyenda: Servicio de pacientes.
    # Responsabilidades: registro, login, lectura de exámenes (legacy), verificación existencia.
    # Próxima migración: usar repositorios para separar persistencia; unificar acceso a exámenes vía workflow.
    def __init__(self, base_dir=None):
        if base_dir is not None:
            from app.config import BASE_DATA_DIR as GLOBAL_BASE
            # Reasignar BASE_DATA_DIR dinámicamente para este servicio no es trivial; usamos base_dir explícito.
            self.paciente_manager = PacienteManager(base_dir=base_dir)
            self.admin_manager = AdminManager(base_dir=base_dir)
            self.examen_workflow = ExamenWorkflowService()
            # Override repos del workflow al mismo base_dir
            self.examen_workflow.solicitud_repo.base_dir = base_dir
            self.examen_workflow.resultado_repo.base_dir = base_dir
        else:
            self.paciente_manager = PacienteManager()
            self.admin_manager = AdminManager()
            self.examen_workflow = ExamenWorkflowService()  # Acceso a resultados workflow

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
                    "nombre_completo": datos_paciente["nombre_completo"],
                    "tipo_usuario": "paciente"
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

    def obtener_examenes_paciente(self, documento: str) -> list:
        """
        Obtiene todos los exámenes de un paciente.
        """
        #legacy = self.admin_manager.listar_examenes_paciente(documento)
        workflow = self.examen_workflow.listar_resultados_paciente(documento)
        normalizados = []
        # for ex in legacy:
        #     normalizados.append({
        #         "codigo": ex.get("codigo_examen"),
        #         "tipo_examen": ex.get("examen_solicitado"),
        #         "codigo_cita": ex.get("codigo_cita"),
        #         "documento_paciente": ex.get("documento_paciente"),
        #         "documento_medico": (ex.get("medico") or {}).get("documento"),
        #         "diagnostico": ex.get("diagnostico"),
        #         "interpretacion": ex.get("diagnostico"),  # legacy no distingue
        #         "valores": ex.get("valores"),
        #         "estado": ex.get("estado"),
        #         "estado_riesgo": None,
        #         "origen": "legacy",
        #         "fecha_registro": ex.get("fecha_registro")
        #     })
        for ex in workflow:
            normalizados.append({
                "codigo": ex.get("id"),
                "tipo_examen": None,  # solicitud inicial guarda tipo en solicitud, no en resultado
                "codigo_cita": ex.get("codigo_cita"),
                "documento_paciente": ex.get("documento_paciente"),
                "documento_medico": ex.get("documento_medico"),
                "diagnostico": None,
                "interpretacion": ex.get("interpretacion"),
                "valores": ex.get("valores"),
                "estado": "resultado",  # resultado consolidado
                "estado_riesgo": ex.get("estado_riesgo"),
                "origen": "workflow",
                "fecha_registro": ex.get("fecha_registro")
            })
        return normalizados

    def obtener_resultado_examen(self, codigo_examen: str) -> dict:
        """
        Obtiene el resultado de un examen específico.
        """
        # Intentar legacy
        ex_legacy = self.admin_manager.obtener_resultado_examen(codigo_examen)
        if ex_legacy:
            return ex_legacy
        # Buscar en resultados workflow (lista completa)
        for r in self.examen_workflow.resultado_repo.list():
            if r.get("id") == codigo_examen or r.get("solicitud_id") == codigo_examen:
                return r
        return None
