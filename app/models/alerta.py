"""Modelo de Alerta.
Relaciones:
- referencia_id: puede apuntar a ExamenResultado.id o Diagnostico.id
- fuente: clasifica el origen para reglas posteriores.
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import datetime
from .base import SeveridadAlerta

class Alerta(BaseModel):
    id: str
    documento_paciente: str
    fuente: str  # "examen" | "diagnostico" | "manual"
    referencia_id: str
    tipo_alerta: str
    severidad: SeveridadAlerta
    fecha_generada: datetime = Field(default_factory=datetime.utcnow)
    estado: str = Field(default="pendiente_vista")  # "pendiente_vista" | "vista"

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

