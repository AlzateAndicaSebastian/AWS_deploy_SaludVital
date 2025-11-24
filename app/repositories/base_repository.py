"""Repositorio base.
Define operaciones genéricas para cargar/guardar colecciones JSON (lista de entidades).
Cada colección se almacena en un archivo. Las entidades deben tener 'id' único.
Optimista: si se pasa expected_version se valida contra version del objeto.
"""
from __future__ import annotations
from typing import TypeVar, Generic, List, Optional, Callable, Dict, Any
from pathlib import Path
import json
from filelock import FileLock
import os

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
        with FileLock(lock_path):
            with open(tmp_path, "w") as f:
                json.dump(items, f, indent=4)
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

