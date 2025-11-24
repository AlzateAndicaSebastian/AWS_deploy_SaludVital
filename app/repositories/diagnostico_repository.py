"""Repositorio de Diagnósticos.
Archivo: diagnosticos.json
"""
from __future__ import annotations
from pathlib import Path
from typing import List
from .base_repository import BaseRepository
from app.models.diagnostico import Diagnostico

class DiagnosticoRepository(BaseRepository[Diagnostico]):
    def __init__(self, base_dir: Path):
        super().__init__(base_dir, "diagnosticos.json")

    def listar_por_paciente(self, documento_paciente: str) -> List[dict]:
        return self.filter(lambda d: d.get("documento_paciente") == documento_paciente)

    def listar_por_medico(self, documento_medico: str) -> List[dict]:
        return self.filter(lambda d: d.get("documento_medico") == documento_medico)

