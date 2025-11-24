"""Modelos relacionados a Exámenes.
Separación:
- ExamenSolicitud: creado por el médico, puede requerir autorización (admin)
- ExamenResultado: datos finales del examen, enlazado a la solicitud
Relaciones:
- solicitud_id en ExamenResultado referencia ExamenSolicitud.id
- codigo_cita y documento_paciente / documento_medico replicados para trazabilidad directa
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict
from .base import EstadoExamen

class ExamenSolicitud(BaseModel):
    id: str
    codigo_cita: str
    documento_paciente: str
    documento_medico: str
    tipo_examen: str
    estado: EstadoExamen = Field(default=EstadoExamen.solicitado)
    fecha_solicitud: datetime = Field(default_factory=datetime.utcnow)
    fecha_autorizacion: Optional[datetime] = None
    fecha_resultado: Optional[datetime] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class ExamenResultado(BaseModel):
    id: str
    solicitud_id: str
    codigo_cita: str
    documento_paciente: str
    documento_medico: str
    valores: Dict[str, float]
    interpretacion: Optional[str] = None
    fecha_registro: datetime = Field(default_factory=datetime.utcnow)
    estado_riesgo: str = Field(default="normal")  # "normal", "alerta", "critico"

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

