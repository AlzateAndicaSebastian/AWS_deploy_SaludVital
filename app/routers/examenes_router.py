from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict
from app.services.examen_workflow_service import ExamenWorkflowService
from app.config import decodificar_token_acceso
from app.security.roles import require_role, Role, get_payload

router = APIRouter(prefix="/examenes", tags=["examenes"])
security = HTTPBearer()
workflow = ExamenWorkflowService()

class CrearSolicitudExamen(BaseModel):
    codigo_cita: str
    documento_paciente: str
    tipo_examen: str

class RegistrarResultado(BaseModel):
    solicitud_id: str
    valores: Dict[str, float]
    interpretacion: str | None = None

class AutorizarSolicitud(BaseModel):
    solicitud_id: str

# Dependencias de rol usando claim tipo_usuario

def verificar_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        return decodificar_token_acceso(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

@router.post("/solicitudes", status_code=status.HTTP_201_CREATED)
async def crear_solicitud(datos: CrearSolicitudExamen, payload: dict = Depends(require_role(Role.medico))):
    try:
        documento_medico = payload.get("documento")
        solicitud = workflow.crear_solicitud(datos.codigo_cita, datos.documento_paciente, documento_medico, datos.tipo_examen)
        return {"solicitud": solicitud}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/solicitudes/autorizar", status_code=status.HTTP_200_OK)
async def autorizar_solicitud(datos: AutorizarSolicitud, payload: dict = Depends(require_role(Role.admin))):
    try:
        respuesta = workflow.autorizar_solicitud(datos.solicitud_id)
        return {"solicitud": respuesta}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/resultados", status_code=status.HTTP_201_CREATED)
async def registrar_resultado(datos: RegistrarResultado, payload: dict = Depends(require_role(Role.admin))):
    try:
        resultado = workflow.registrar_resultado(datos.solicitud_id, datos.valores, datos.interpretacion)
        return {"resultado": resultado}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/paciente/{documento_paciente}")
async def listar_resultados_paciente(documento_paciente: str, payload: dict = Depends(get_payload)):
    try:
        # Permitir a paciente consultar los suyos y médico/admin ver cualquiera
        if payload.get("tipo_usuario") in [Role.medico.value, Role.admin.value] or payload.get("documento") == documento_paciente:
            resultados = workflow.listar_resultados_paciente(documento_paciente)
            return {"resultados": resultados}
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso restringido")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/solicitudes/paciente/{documento_paciente}")
async def listar_solicitudes_paciente(documento_paciente: str, codigo_cita: str | None = None, estado: str | None = None, payload: dict = Depends(get_payload)):
    """Lista las solicitudes de examen de un paciente.
    Filtros opcionales:
    - codigo_cita: restringe a una cita específica
    - estado: filtra por estado del flujo (solicitado, autorizado, procesando, resultado)
    Permisos:
    - Paciente: solo sus propias solicitudes
    - Médico/Admin: cualquier paciente
    """
    try:
        tipo = payload.get("tipo_usuario")
        if tipo in [Role.medico.value, Role.admin.value] or payload.get("documento") == documento_paciente:
            solicitudes = workflow.listar_solicitudes_paciente(documento_paciente, codigo_cita=codigo_cita, estado=estado)
            return {"solicitudes": solicitudes}
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso restringido")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
