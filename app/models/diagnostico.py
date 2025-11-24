"""Modelo de Diagnóstico.
Relaciones:
- codigo_cita: vínculo obligatorio a Cita
- documento_medico: médico que emite el diagnóstico
- documento_paciente: redundante para facilitar consultas (evita join futuro)
- examenes_solicitados: lista de IDs de ExamenSolicitud (a crear posteriormente)
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Diagnostico(BaseModel):
    id: str
    codigo_cita: str
    documento_medico: str
    documento_paciente: str
    descripcion: str
    observaciones: Optional[str] = None
    examenes_solicitados: List[str] = Field(default_factory=list)
    fecha_registro: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

