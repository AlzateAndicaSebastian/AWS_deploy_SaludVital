"""Modelo de Cita.
Relaciones:
- documento_paciente: referencia a Paciente
- documento_medico: referencia a Medico
- diagnostico_id: (opcional) referencia a Diagnostico
Workflow manejado por EstadoCita (ver base.py)
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .base import EstadoCita

class Cita(BaseModel):
    codigo_cita: str
    documento_paciente: str
    documento_medico: str
    paciente_nombre: str
    medico_nombre: str
    fecha_programada: datetime
    registrado: datetime = Field(default_factory=datetime.utcnow)
    estado: EstadoCita = Field(default=EstadoCita.agendada)
    tipo_cita: str
    motivo_paciente: str
    prioridad: int
    diagnostico_id: Optional[str] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

