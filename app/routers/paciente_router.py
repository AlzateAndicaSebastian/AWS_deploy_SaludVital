from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.services.paciente_service import PacienteService

router = APIRouter(prefix="/pacientes", tags=["pacientes"])

# Servicio para manejar las operaciones de pacientes
paciente_service = PacienteService()


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