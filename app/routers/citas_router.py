from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import os
from app.services.citas_service import CitasService
from app.config import decodificar_token_acceso, verificar_documento_paciente

router = APIRouter(prefix="/citas", tags=["citas"])

# Servicio para manejar las citas
citas_service = CitasService()

# Seguridad con token Bearer
security = HTTPBearer()

# Modelo para la creación de citas
class CrearCitaRequest(BaseModel):
    paciente: str
    medico: str
    fecha: str
    documento: str
    tipoCita: str
    motivoPaciente: str

# Modelo para la eliminación de citas
class EliminarCitaRequest(BaseModel):
    paciente: str
    medico: str
    fecha: str
    documento: str

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
    datos_cita: CrearCitaRequest,
    payload: dict = Depends(verificar_token)
):
    """
    Crea una nueva cita para un paciente.
    
    Requiere un token válido que contenga el documento del paciente.
    Verifica que el paciente esté registrado antes de crear la cita.
    """
    # Verificar que el documento del token coincida con el documento proporcionado
    if payload.get("documento") != datos_cita.documento:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para crear citas para este paciente",
        )
    
    # Verificar que el paciente esté registrado
    verificar_paciente_registrado(datos_cita.documento)
    
    try:
        cita = citas_service.crear_cita_service(
            datos_cita.paciente,
            datos_cita.medico,
            datos_cita.fecha,
            datos_cita.documento,
            datos_cita.tipoCita,
            datos_cita.motivoPaciente
        )
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
    datos_eliminacion: EliminarCitaRequest,
    payload: dict = Depends(verificar_token)
):
    """
    Elimina una cita específica de un paciente.
    
    Requiere un token válido que contenga el documento del paciente.
    Verifica que el paciente esté registrado antes de eliminar la cita.
    """
    # Verificar que el documento del token coincida con el documento proporcionado
    if payload.get("documento") != datos_eliminacion.documento:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar citas de este paciente",
        )
    
    # Verificar que el paciente esté registrado
    verificar_paciente_registrado(datos_eliminacion.documento)
    
    try:
        resultado = citas_service.eliminar_cita_service(
            datos_eliminacion.paciente,
            datos_eliminacion.medico,
            datos_eliminacion.fecha,
            datos_eliminacion.documento
        )
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
    payload: dict = Depends(verificar_token) # valida que solo los pacientes autenticados puedan acceder a sus citas
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