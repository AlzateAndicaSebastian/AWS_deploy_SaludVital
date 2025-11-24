"""
Utilidades de escritura/lectura atómica sobre archivos JSON.
Se crea primero un archivo temporal y luego se reemplaza (os.replace) para asegurar
que nunca haya estados intermedios corruptos. Pensado para poder cambiar
fácilmente a otra capa de persistencia (por ejemplo SQL) reemplazando estas funciones
por adaptadores que ignoren el sistema de archivos.
"""
from __future__ import annotations
import os
import json
from typing import Any, Dict
from filelock import FileLock


def atomic_write_json(path: str, data: Dict[str, Any]) -> None:
    """Escribe un JSON en disco de forma atómica.
    Pasos:
      1. Crea <path>.tmp
      2. Escribe JSON con indent=4
      3. os.replace para asegurar operación atómica en la mayoría de FS.
    """
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w") as f:
        json.dump(data, f, indent=4)
    os.replace(tmp_path, path)


def atomic_load_json(path: str) -> Dict[str, Any] | None:
    """Carga un JSON si existe, retornando dict o None si no existe / error."""
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return None


def locked_atomic_write(path: str, data: Dict[str, Any]) -> None:
    """Envuelve atomic_write_json bajo FileLock para evitar intercalado de escrituras."""
    lock_path = f"{path}.lock"
    with FileLock(lock_path):
        atomic_write_json(path, data)


def locked_atomic_load(path: str) -> Dict[str, Any] | None:
    """Lectura protegida por FileLock (consistente con escrituras)."""
    lock_path = f"{path}.lock"
    with FileLock(lock_path):
        return atomic_load_json(path)

