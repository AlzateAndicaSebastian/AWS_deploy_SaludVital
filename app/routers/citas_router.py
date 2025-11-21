from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from app.services.citas_service import CitasService
from app.config import decodificar_token_acceso, verificar_documento_paciente

router = APIRouter(prefix="/citas", tags=["citas"])

# Servicio para manejar las citas
citas_service = CitasService()

# Seguridad con token Bearer
security = HTTPBearer()

def verificar_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verifica el token de acceso y devuelve el payload si es válido.
    """
    try:
        payload = decodificar_token_acceso(credentials.credentials)
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

def verificar_paciente_registrado(documento: str):
    """
    Verifica si el paciente está registrado.
    """
    if not verificar_documento_paciente(documento):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Paciente no registrado",
        )
    return True

@router.post("/")
async def crear_cita(
    paciente: str,
    medico: str,
    fecha: str,
    documento: str,
    tipoCita: str,
    motivoPaciente: str,
    payload: dict = Depends(verificar_token)
):
    """
    Crea una nueva cita para un paciente.
    
    Requiere un token válido que contenga el documento del paciente.
    Verifica que el paciente esté registrado antes de crear la cita.
    """
    # Verificar que el documento del token coincida con el documento proporcionado
    if payload.get("documento") != documento:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para crear citas para este paciente",
        )
    
    # Verificar que el paciente esté registrado
    verificar_paciente_registrado(documento)
    
    try:
        cita = citas_service.crear_cita_service(paciente, medico, fecha, documento, tipoCita, motivoPaciente)
        return {"mensaje": "Cita creada exitosamente", "cita": cita}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la cita: {str(e)}"
        )

@router.delete("/")
async def eliminar_cita(
    paciente: str,
    medico: str,
    fecha: str,
    documento: str,
    payload: dict = Depends(verificar_token)
):
    """
    Elimina una cita específica de un paciente.
    
    Requiere un token válido que contenga el documento del paciente.
    Verifica que el paciente esté registrado antes de eliminar la cita.
    """
    # Verificar que el documento del token coincida con el documento proporcionado
    if payload.get("documento") != documento:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar citas de este paciente",
        )
    
    # Verificar que el paciente esté registrado
    verificar_paciente_registrado(documento)
    
    try:
        resultado = citas_service.eliminar_cita_service(paciente, medico, fecha, documento)
        if resultado:
            return {"mensaje": "Cita eliminada exitosamente"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cita no encontrada"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar la cita: {str(e)}"
        )

@router.get("/{documento}")
async def obtener_citas_paciente(
    documento: str,
    payload: dict = Depends(verificar_token)
):
    """
    Obtiene todas las citas de un paciente.
    
    Requiere un token válido que contenga el documento del paciente.
    Verifica que el paciente esté registrado antes de devolver las citas.
    """
    # Verificar que el documento del token coincida con el documento proporcionado
    if payload.get("documento") != documento:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a las citas de este paciente",
        )
    
    # Verificar que el paciente esté registrado
    verificar_paciente_registrado(documento)
    
    try:
        citas = citas_service.obtener_citas_paciente_service(documento)
        return {"citas": citas}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener las citas: {str(e)}"
        )