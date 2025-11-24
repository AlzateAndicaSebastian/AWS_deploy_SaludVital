"""Repositorio de Citas.
Archivo: citas.json almacena todas las citas (se puede fragmentar por paciente en futuro).
Relación con modelos: usa estructura directa del modelo Cita (dict).
"""
from __future__ import annotations
from pathlib import Path
from typing import List, Optional
from .base_repository import BaseRepository
from app.models.cita import Cita

class CitaRepository(BaseRepository[Cita]):
    def __init__(self, base_dir: Path):
        super().__init__(base_dir, "citas.json")

    def listar_citas_paciente(self, documento_paciente: str) -> List[dict]:
        return self.filter(lambda c: c.get("documento_paciente") == documento_paciente)

    def listar_citas_medico(self, documento_medico: str) -> List[dict]:
        return self.filter(lambda c: c.get("documento_medico") == documento_medico)

    def obtener_por_codigo(self, codigo_cita: str) -> Optional[dict]:
        return self.get(codigo_cita)

