"""Servicio de workflow de Exámenes.
Responsabilidad:
- Crear solicitudes de examen ligadas a cita
- Autorizar / rechazar (rol admin)
- Registrar resultado (rol admin/lab) y evaluar riesgo
Relaciones:
- Usa repositorios de ExamenSolicitud y ExamenResultado
- Interactúa potencialmente con AlertaService para generar alertas por resultado crítico
"""
from __future__ import annotations
from typing import Dict, Any
from uuid import uuid4
from datetime import datetime, timezone
from app.config import BASE_DATA_DIR
from app.repositories.examen_repository import ExamenSolicitudRepository, ExamenResultadoRepository
from app.models.examen import ExamenSolicitud, ExamenResultado
from app.models.base import EstadoExamen
from app.metrics.metrics import inc_examen_solicitado

class ExamenWorkflowService:
    # Leyenda: Orquesta el ciclo de vida de un examen.
    # No implementa reglas complejas de alertas; delega a un servicio especializado.
    # Agnóstico de la fuente de datos: repositorios pueden migrar a SQL sin cambiar este servicio.
    def __init__(self):
        self.solicitud_repo = ExamenSolicitudRepository(BASE_DATA_DIR)
        self.resultado_repo = ExamenResultadoRepository(BASE_DATA_DIR)

    def crear_solicitud(self, codigo_cita: str, documento_paciente: str, documento_medico: str, tipo_examen: str) -> Dict[str, Any]:
        solicitud = ExamenSolicitud(
            id=str(uuid4()),
            codigo_cita=codigo_cita,
            documento_paciente=documento_paciente,
            documento_medico=documento_medico,
            tipo_examen=tipo_examen
        )
        self.solicitud_repo.insert(solicitud.model_dump())
        inc_examen_solicitado()
        return solicitud.model_dump()

    def autorizar_solicitud(self, solicitud_id: str) -> Dict[str, Any]:
        updated = self.solicitud_repo.update(solicitud_id, lambda s: self._transicion_autorizar(s))
        if not updated:
            raise ValueError("Solicitud no encontrada")
        return updated

    def _transicion_autorizar(self, solicitud: Dict[str, Any]) -> Dict[str, Any]:
        if solicitud.get("estado") != EstadoExamen.solicitado:
            raise ValueError("Estado inválido para autorización")
        solicitud["estado"] = EstadoExamen.autorizado
        solicitud["fecha_autorizacion"] = datetime.now(timezone.utc).isoformat()
        return solicitud

    def registrar_resultado(self, solicitud_id: str, valores: Dict[str, float], interpretacion: str | None = None) -> Dict[str, Any]:
        solicitud = self.solicitud_repo.get(solicitud_id)
        if not solicitud:
            raise ValueError("Solicitud no encontrada")
        if solicitud.get("estado") not in [EstadoExamen.autorizado, EstadoExamen.procesando]:
            raise ValueError("No se puede registrar resultado en el estado actual")
        resultado = ExamenResultado(
            id=str(uuid4()),
            solicitud_id=solicitud_id,
            codigo_cita=solicitud["codigo_cita"],
            documento_paciente=solicitud["documento_paciente"],
            documento_medico=solicitud["documento_medico"],
            valores=valores,
            interpretacion=interpretacion,
            estado_riesgo=self._evaluar_riesgo(valores)
        )
        self.resultado_repo.insert(resultado.model_dump())
        self.solicitud_repo.update(solicitud_id, lambda s: self._transicion_resultado(s))
        return resultado.model_dump()

    def _transicion_resultado(self, solicitud: Dict[str, Any]) -> Dict[str, Any]:
        solicitud["estado"] = EstadoExamen.resultado
        solicitud["fecha_resultado"] = datetime.now(timezone.utc).isoformat()
        return solicitud

    def _evaluar_riesgo(self, valores: Dict[str, float]) -> str:
        niveles = [v for v in valores.values()]
        if any(v > 180 for v in niveles):
            return "critico"
        if any(v > 140 for v in niveles):
            return "alerta"
        return "normal"

    def listar_resultados_paciente(self, documento_paciente: str) -> list:
        return self.resultado_repo.listar_por_paciente(documento_paciente)

    def listar_solicitudes_paciente(self, documento_paciente: str, codigo_cita: str | None = None, estado: str | None = None) -> list:
        """Lista solicitudes de examen de un paciente.
        Opcionalmente filtra por código de cita y/o estado (solicitado, autorizado, procesando, resultado).
        """
        solicitudes = self.solicitud_repo.listar_por_paciente(documento_paciente)
        if codigo_cita:
            solicitudes = [s for s in solicitudes if s.get("codigo_cita") == codigo_cita]
        if estado:
            solicitudes = [s for s in solicitudes if s.get("estado") == estado]
        return solicitudes
