from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from app.services.medico_service import MedicoService
from app.config import decodificar_token_acceso
from app.security.roles import require_role, Role, get_payload

router = APIRouter(prefix="/medicos", tags=["medicos"])

# Servicio para manejar las operaciones de médicos
medico_service = MedicoService()

# Seguridad con token Bearer
security = HTTPBearer()

class RegistroMedico(BaseModel):
    documento: str
    nombre_completo: str
    contraseña: str
    telefono: str
    email: str
    especialidad: str

class LoginMedico(BaseModel):
    documento: str
    contraseña: str

class Diagnostico(BaseModel):
    codigo_cita: str
    descripcion: str
    observaciones: Optional[str] = None
    examenes_solicitados: Optional[List[str]] = None

class CerrarCitaRequest(BaseModel):
    codigo_cita: str
    estado: str  # "realizada", "cancelada", "noAsistida"
    diagnostico: Optional[Diagnostico] = None

@router.post("/registro", status_code=status.HTTP_201_CREATED)
async def registrar_medico(datos: RegistroMedico):
    """
    Registra un nuevo médico en el sistema.
    Solo accesible por administradores en implementaciones futuras.
    """
    try:
        medico_service.registrar_medico(
            datos.documento,
            datos.nombre_completo,
            datos.contraseña,
            datos.telefono,
            datos.email,
            datos.especialidad
        )
        return {"mensaje": "Médico registrado exitosamente"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/login")
async def login_medico(credenciales: LoginMedico):
    """
    Autentica a un médico y devuelve un token de acceso.
    """
    try:
        resultado = medico_service.login_medico(
            credenciales.documento,
            credenciales.contraseña
        )
        return resultado
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/agenda")
async def obtener_agenda(payload: dict = Depends(require_role(Role.medico))):
    """
    Obtiene la agenda de un médico con sus citas futuras.
    """
    try:
        documento_medico = payload.get("documento")
        agenda = medico_service.obtener_agenda_medico(documento_medico)
        return {"agenda": agenda}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la agenda: {str(e)}"
        )

@router.post("/cerrar-cita")
async def cerrar_cita(
    datos_cierre: CerrarCitaRequest,
    payload: dict = Depends(require_role(Role.medico))
):
    """
    Cierra una cita con un estado específico. Si el estado es 'realizada',
    se puede incluir un diagnóstico.
    """
    try:
        documento_medico = payload.get("documento")
        diagnostico_dict = datos_cierre.diagnostico.dict() if datos_cierre.diagnostico else None
        resultado = medico_service.cerrar_cita(
            documento_medico,
            datos_cierre.codigo_cita,
            datos_cierre.estado,
            diagnostico_dict
        )
        return {"mensaje": "Cita cerrada exitosamente", "resultado": resultado}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cerrar la cita: {str(e)}"
        )

@router.get("/diagnosticos/{codigo_cita}")
async def obtener_diagnostico(
    codigo_cita: str,
    payload: dict = Depends(require_role(Role.medico))
):
    """
    Obtiene el diagnóstico de una cita específica.
    """
    try:
        diagnostico = medico_service.obtener_diagnostico(codigo_cita)
        if not diagnostico:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diagnóstico no encontrado"
            )
        return {"diagnostico": diagnostico}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el diagnóstico: {str(e)}"
        )