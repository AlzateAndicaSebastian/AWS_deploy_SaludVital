"""Base de modelos Pydantic y enums compartidos.
Cada modelo incluye un campo 'version' para soporte de control optimista de concurrencia.
En una futura migración a SQL, estos modelos podrán mapearse a ORM sin modificar
los servicios (adaptador repositorio cambia, no el modelo).
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from typing import Optional

class EstadoCita(str, Enum):
    agendada = "agendada"
    en_curso = "en_curso"
    atendida = "atendida"
    cerrada = "cerrada"
    cancelada = "cancelada"

class EstadoExamen(str, Enum):
    solicitado = "solicitado"
    autorizado = "autorizado"
    procesando = "procesando"
    resultado = "resultado"
    cerrado = "cerrado"
    rechazado = "rechazado"

class SeveridadAlerta(str, Enum):
    info = "info"
    advertencia = "advertencia"
    critica = "critica"

class BaseDomainModel(BaseModel):
    """Modelo base para todas las entidades de dominio.
    version: soporte para control de concurrencia optimista.
    created_at / updated_at: timestamps para auditoría básica.
    """
    version: int = Field(default=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def bump_version(self) -> None:
        object.__setattr__(self, "version", self.version + 1)
        object.__setattr__(self, "updated_at", datetime.utcnow())

    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True

