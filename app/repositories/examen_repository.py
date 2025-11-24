"""Repositorio de Exámenes (solicitudes y resultados).
Archivo: examenes_solicitudes.json / examenes_resultados.json
Se separan para no mezclar estados y simplificar iteraciones futuras.
"""
from __future__ import annotations
from pathlib import Path
from typing import List
from .base_repository import BaseRepository
from app.models.examen import ExamenSolicitud, ExamenResultado

class ExamenSolicitudRepository(BaseRepository[ExamenSolicitud]):
    def __init__(self, base_dir: Path):
        super().__init__(base_dir, "examenes_solicitudes.json")

    def listar_por_paciente(self, documento_paciente: str) -> List[dict]:
        return self.filter(lambda e: e.get("documento_paciente") == documento_paciente)

    def listar_por_medico(self, documento_medico: str) -> List[dict]:
        return self.filter(lambda e: e.get("documento_medico") == documento_medico)

class ExamenResultadoRepository(BaseRepository[ExamenResultado]):
    def __init__(self, base_dir: Path):
        super().__init__(base_dir, "examenes_resultados.json")

    def listar_por_paciente(self, documento_paciente: str) -> List[dict]:
        return self.filter(lambda e: e.get("documento_paciente") == documento_paciente)

    def listar_por_medico(self, documento_medico: str) -> List[dict]:
        return self.filter(lambda e: e.get("documento_medico") == documento_medico)

