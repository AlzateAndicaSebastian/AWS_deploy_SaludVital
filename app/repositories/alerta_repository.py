"""Repositorio de Alertas.
Archivo: alertas.json
Permite listar por paciente.
"""
from __future__ import annotations
from pathlib import Path
from typing import List
from .base_repository import BaseRepository
from app.models.alerta import Alerta

class AlertaRepository(BaseRepository[Alerta]):
    def __init__(self, base_dir: Path):
        super().__init__(base_dir, "alertas.json")

    def listar_por_paciente(self, documento_paciente: str) -> List[dict]:
        return self.filter(lambda a: a.get("documento_paciente") == documento_paciente)

