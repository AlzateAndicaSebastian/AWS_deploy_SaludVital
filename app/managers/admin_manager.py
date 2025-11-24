import json
import os
from datetime import datetime
from pathlib import Path
from filelock import FileLock
from app.config import BASE_DATA_DIR


class AdminManager:
    def __init__(self, base_dir=None):
        """
        Gestiona las operaciones administrativas, especialmente los resultados de exámenes.
        base_dir permite aislar el almacenamiento (útil en tests).
        """
        self.base_dir = base_dir or BASE_DATA_DIR
        
        # Directorio para almacenar los resultados de exámenes
        self.examenes_dir = self.base_dir / "examenes"
        self.examenes_dir.mkdir(parents=True, exist_ok=True)

    def crear_resultado_examen(self, codigo_examen: str, datos_examen: dict):
        """
        Crea un resultado de examen con los datos proporcionados.
        """
        archivo = self.examenes_dir / f"{codigo_examen}.json"
        lock_path = str(archivo) + ".lock"
        
        # Agregar marca de tiempo
        datos_examen["fecha_registro"] = datetime.now().isoformat()
        datos_examen["codigo_examen"] = codigo_examen
        
        with FileLock(lock_path):
            with open(archivo, "w") as f:
                json.dump(datos_examen, f, indent=4)

    def obtener_resultado_examen(self, codigo_examen: str) -> dict:
        """
        Obtiene el resultado de un examen específico.
        """
        archivo = self.examenes_dir / f"{codigo_examen}.json"
        lock_path = str(archivo) + ".lock"
        
        if not os.path.exists(archivo):
            return None

        with FileLock(lock_path):
            try:
                with open(archivo, "r") as f:
                    return json.load(f)
            except Exception:
                return None

    def listar_examenes_paciente(self, documento_paciente: str) -> list:
        """
        Lista todos los exámenes de un paciente específico.
        """
        examenes = []
        
        # Recorrer todos los archivos de exámenes
        for archivo in self.examenes_dir.iterdir():
            if archivo.is_file() and archivo.suffix == '.json':
                with FileLock(str(archivo) + ".lock"):
                    try:
                        with open(archivo, "r") as f:
                            examen = json.load(f)
                            # Verificar si el examen pertenece al paciente
                            if examen.get("documento_paciente") == documento_paciente:
                                examenes.append(examen)
                    except Exception:
                        # Ignorar archivos que no se pueden leer
                        continue
                        
        return examenes

    def actualizar_estado_examen(self, codigo_examen: str, estado: str, 
                                 observaciones: str = None) -> bool:
        """
        Actualiza el estado de un examen (por ejemplo: pendiente, en proceso, completado, crítico).
        """
        examen = self.obtener_resultado_examen(codigo_examen)
        if not examen:
            return False
            
        examen["estado"] = estado
        if observaciones:
            examen["observaciones"] = observaciones
            
        archivo = self.examenes_dir / f"{codigo_examen}.json"
        lock_path = str(archivo) + ".lock"
        
        with FileLock(lock_path):
            with open(archivo, "w") as f:
                json.dump(examen, f, indent=4)
                
        return True
