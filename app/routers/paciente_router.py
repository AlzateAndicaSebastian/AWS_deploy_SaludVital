from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from app.services.paciente_service import PacienteService
from app.config import decodificar_token_acceso

router = APIRouter(prefix="/pacientes", tags=["pacientes"])

# Servicio para manejar las operaciones de pacientes
paciente_service = PacienteService()

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


class RegistroPaciente(BaseModel):
    documento: str
    nombre_completo: str
    contraseña: str
    telefono: str
    email: str
    edad: int
    sexo: str


class LoginPaciente(BaseModel):
    documento: str
    contraseña: str


@router.post("/registro", status_code=status.HTTP_201_CREATED)
async def registrar_paciente(datos: RegistroPaciente):
    """
    Registra un nuevo paciente en el sistema.
    """
    try:
        paciente_service.registrar_paciente(
            datos.documento,
            datos.nombre_completo,
            datos.contraseña,
            datos.telefono,
            datos.email,
            datos.edad,
            datos.sexo
        )
        return {"mensaje": "Paciente registrado exitosamente"}
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


@router.get("/examenes")
async def obtener_examenes_paciente(payload: dict = Depends(verificar_token)):
    """
    Obtiene todos los exámenes del paciente autenticado.
    """
    try:
        documento_paciente = payload.get("documento")
        examenes = paciente_service.obtener_examenes_paciente(documento_paciente)
        return {"examenes": examenes}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los exámenes: {str(e)}"
        )


@router.get("/examenes/{codigo_examen}")
async def obtener_resultado_examen(
    codigo_examen: str,
    payload: dict = Depends(verificar_token)
):
    """
    Obtiene el resultado de un examen específico.
    """
    try:
        # Verificar que el examen pertenezca al paciente
        documento_paciente = payload.get("documento")
        examen = paciente_service.obtener_resultado_examen(codigo_examen)
        
        if not examen:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Examen no encontrado"
            )
            
        # Verificar que el examen pertenezca al paciente autenticado
        if examen.get("documento_paciente") != documento_paciente:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para acceder a este examen"
            )
            
        return {"examen": examen}
    except HTTPException:
        # Relanzar las excepciones HTTP ya formateadas
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el resultado del examen: {str(e)}"
        )


@router.post("/login")
async def login_paciente(credenciales: LoginPaciente):
    """
    Autentica a un paciente y devuelve un token de acceso.
    """
    try:
        resultado = paciente_service.login_paciente(
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