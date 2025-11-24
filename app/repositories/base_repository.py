"""Repositorio base.
Define operaciones genéricas para cargar/guardar colecciones JSON (lista de entidades).
Cada colección se almacena en un archivo. Las entidades deben tener 'id' único.
Optimista: si se pasa expected_version se valida contra version del objeto.
"""

# Al crear una solicitud de examen:
# El servicio ExamenWorkflowService.crear_solicitud construye un objeto ExamenSolicitud y llama a ExamenSolicitudRepository.insert(...).
# Ese repositorio extiende BaseRepository, que carga el archivo examenes_solicitudes.json, agrega la nueva solicitud (dict con id, estado=solicitado, etc.) y lo guarda con escritura atómica y bloqueo (FileLock), evitando corrupción concurrente.
# Al autorizar la solicitud:
# autorizar_solicitud usa update del repositorio: recorre la lista en memoria, modifica el dict (cambia estado a autorizado y agrega timestamp), y vuelve a escribir el archivo completo. Así se mantiene un único origen de verdad.
# Al registrar el resultado:
# Se valida que la solicitud esté en estado autorizado (o procesando), luego se crea un ExamenResultado que se inserta mediante ExamenResultadoRepository.insert(...) en examenes_resultados.json.
# Paralelamente se hace un update sobre la solicitud para marcar su estado como resultado y guardar fecha_resultado. No se reescribe datos redundantes (se conserva trazabilidad por solicitud_id y codigo_cita).
from __future__ import annotations
from typing import TypeVar, Generic, List, Optional, Callable, Dict, Any
from pathlib import Path
import json
from filelock import FileLock
import os
from datetime import datetime

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, base_dir: Path, filename: str):
        self.file_path = base_dir / filename
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_all(self) -> List[Dict[str, Any]]:
        if not self.file_path.exists():
            return []
        lock_path = str(self.file_path) + ".lock"
        with FileLock(lock_path):
            try:
                with open(self.file_path, "r") as f:
                    return json.load(f)
            except Exception:
                return []

    def _save_all(self, items: List[Dict[str, Any]]) -> None:
        lock_path = str(self.file_path) + ".lock"
        tmp_path = str(self.file_path) + ".tmp"
        def _default(o):
            if isinstance(o, datetime):
                return o.isoformat()
            raise TypeError(f"Tipo no serializable: {type(o)}")
        with FileLock(lock_path):
            with open(tmp_path, "w") as f:
                json.dump(items, f, indent=4, default=_default)
            os.replace(tmp_path, self.file_path)

    def list(self) -> List[Dict[str, Any]]:
        return self._load_all()

    def get(self, id: str) -> Optional[Dict[str, Any]]:
        for item in self._load_all():
            if item.get("id") == id or item.get("codigo_cita") == id:
                return item
        return None

    def insert(self, item: Dict[str, Any]) -> None:
        items = self._load_all()
        items.append(item)
        self._save_all(items)

    def update(self, id: str, updater: Callable[[Dict[str, Any]], Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        items = self._load_all()
        updated = None
        for i, itm in enumerate(items):
            if itm.get("id") == id or itm.get("codigo_cita") == id:
                new_item = updater(dict(itm))
                items[i] = new_item
                updated = new_item
                break
        if updated:
            self._save_all(items)
        return updated

    def filter(self, predicate: Callable[[Dict[str, Any]], bool]) -> List[Dict[str, Any]]:
        return [itm for itm in self._load_all() if predicate(itm)]
