"""Módulo centralizado de verificación de seguridad y roles.
Leyenda / Transferencia de conocimiento:
- Este módulo abstrae la verificación de JWT y control de acceso por rol.
- Admite una futura migración a scopes granulares (e.g. 'examen:create').
- Las dependencias FastAPI aquí definidas se usan en los routers para evitar lógica duplicada.
- Para extender: agregar Enum de scopes y un validador adicional que lea un claim 'scopes'.
Advertencia: No almacenar lógica de negocio aquí, solo autorizaciones.
"""
from __future__ import annotations
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from enum import Enum
from typing import Callable, List, Dict
from app.config import decodificar_token_acceso

security = HTTPBearer()

class Role(str, Enum):
    paciente = "paciente"
    medico = "medico"
    admin = "admin"

# ------------------ Utilidades internas ------------------

def _decode_token(credentials: HTTPAuthorizationCredentials) -> Dict:
    try:
        payload = decodificar_token_acceso(credentials.credentials)
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ------------------ Dependencias públicas ------------------

def get_payload(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Decodifica el token y retorna el payload completo. No aplica restricciones de rol."""
    return _decode_token(credentials)

def require_role(*roles: Role) -> Callable:
    """Crea una dependencia que verifica que el claim tipo_usuario esté entre los roles permitidos.
    Uso:
        @router.get('/recurso')
        async def recurso(payload: dict = Depends(require_role(Role.medico, Role.admin))):
            ...
    """
    def _dep(payload: Dict = Depends(get_payload)) -> Dict:
        tipo = payload.get("tipo_usuario")
        if tipo not in [r.value for r in roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado para este rol"
            )
        return payload
    return _dep

def require_same_document_or_roles(roles: List[Role]) -> Callable:
    """Permite acceso si el usuario tiene uno de los roles dados o si el documento en el token
    coincide con el recurso solicitado (se debe pasar 'documento' como argumento en endpoint)."""
    def _dep(documento: str, payload: Dict = Depends(get_payload)) -> Dict:
        tipo = payload.get("tipo_usuario")
        if tipo in [r.value for r in roles] or payload.get("documento") == documento:
            return payload
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso restringido")
    return _dep

# ------------------ Extensión futura ------------------
# def require_scopes(*scopes: str):
#     pass  # Leer claim 'scopes' y validar.

