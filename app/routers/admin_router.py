import os

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from app.services.admin_service import AdminService
from app.config import decodificar_token_acceso
from app.security.roles import require_role, Role

router = APIRouter(prefix="/admin", tags=["administradores"])

# Servicio para manejar las operaciones de administradores
admin_service = AdminService()

# Seguridad con token Bearer
security = HTTPBearer()

# Clave secreta para administradores (debería estar en variables de entorno)
ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY", "admin")

class AdminLogin(BaseModel):
    username: str
    password: str

class ResultadoExamen(BaseModel):
    documento_paciente: str
    paciente: str
    codigo_cita: str
    examen_solicitado: str
    diagnostico: str
    estado: str
    observaciones: Optional[str] = None
    valores: Optional[dict] = None

class ActualizarEstadoExamen(BaseModel):
    estado: str
    observaciones: Optional[str] = None

def verificar_token_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verifica el token de acceso para administradores.
    """
    try:
        payload = decodificar_token_acceso(credentials.credentials)
        # Verificar que sea un token de administrador
        if payload.get("tipo_usuario") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado. Se requiere privilegios de administrador.",
            )
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/login")
async def login_admin(credenciales: AdminLogin):
    """
    Autentica a un administrador y devuelve un token de acceso.
    """
    try:
        resultado = admin_service.login_admin(
            credenciales.username,
            credenciales.password
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


@router.post("/examenes/{codigo_examen}", status_code=status.HTTP_201_CREATED)
async def crear_resultado_examen(
    codigo_examen: str,
    datos_examen: ResultadoExamen,
    payload: dict = Depends(require_role(Role.admin))
):
    """
    Crea un resultado de examen.
    """
    try:
        admin_service.crear_resultado_examen(codigo_examen, datos_examen.dict())
        return {"mensaje": "Resultado de examen creado exitosamente"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el resultado del examen: {str(e)}"
        )


@router.get("/examenes/{codigo_examen}")
async def obtener_resultado_examen(
    codigo_examen: str,
    payload: dict = Depends(require_role(Role.admin))
):
    """
    Obtiene el resultado de un examen específico.
    """
    try:
        examen = admin_service.obtener_resultado_examen(codigo_examen)
        if not examen:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Examen no encontrado"
            )
        return {"examen": examen}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el resultado del examen: {str(e)}"
        )


@router.put("/examenes/{codigo_examen}/estado")
async def actualizar_estado_examen(
    codigo_examen: str,
    datos_actualizacion: ActualizarEstadoExamen,
    payload: dict = Depends(require_role(Role.admin))
):
    """
    Actualiza el estado de un examen.
    """
    try:
        resultado = admin_service.actualizar_estado_examen(
            codigo_examen,
            datos_actualizacion.estado,
            datos_actualizacion.observaciones
        )
        if not resultado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Examen no encontrado"
            )
        return {"mensaje": "Estado del examen actualizado exitosamente"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el estado del examen: {str(e)}"
        )


@router.get("/pacientes/{documento_paciente}/examenes")
async def listar_examenes_paciente(
    documento_paciente: str,
    payload: dict = Depends(require_role(Role.admin))
):
    """
    Lista todos los exámenes de un paciente específico.
    """
    try:
        examenes = admin_service.listar_examenes_paciente(documento_paciente)
        return {"examenes": examenes}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los exámenes del paciente: {str(e)}"
        )

@router.get("/dashboard")
async def admin_dashboard(payload: dict = Depends(require_role(Role.admin))):
    """
    Dashboard de administrador protegido.
    """
    return {"mensaje": "Bienvenido al panel de administrador", "data": payload}

# Eliminado endpoint /admin/registro (modo único administrador por entorno)
# Leyenda: Para crear/rotar credenciales, ajustar variables ADMIN_USERNAME y ADMIN_SECRET_KEY fuera del API.
