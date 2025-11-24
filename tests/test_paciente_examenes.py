import tempfile
from app.services.paciente_service import PacienteService
from app.services.examen_workflow_service import ExamenWorkflowService
from app.managers.admin_manager import AdminManager
from app.managers.paciente_manager import PacienteManager
from app.config import BASE_DATA_DIR
from pathlib import Path
import os
import shutil

# Tests básicos de integración mínima para ver exámenes combinados

def _setup_tmp_dir():
    tmp = tempfile.mkdtemp()
    return Path(tmp)

def test_paciente_examenes_fusion_workflow_legacy(monkeypatch):
    base = _setup_tmp_dir()
    # Instancias aisladas utilizando base_dir común
    paciente_manager = PacienteManager(base_dir=base)
    admin_manager = AdminManager(base_dir=base)
    workflow = ExamenWorkflowService()
    # Reasignar repos al base_dir
    workflow.solicitud_repo.file_path = base / 'examenes_solicitudes.json'
    workflow.resultado_repo.file_path = base / 'examenes_resultados.json'
    service = PacienteService(base_dir=base)

    # Registrar paciente
    documento = "PX001"
    paciente_manager.registrar_paciente(documento, "Paciente X", "clave", "3000000000", "px@example.com", 40, "Masculino")

    # Crear solicitud workflow (simula cita cerrada)
    solicitud = workflow.crear_solicitud("CITA123", documento, "M001", "Glucosa")
    workflow.autorizar_solicitud(solicitud["id"])
    resultado = workflow.registrar_resultado(solicitud["id"], {"glucosa": 150}, "Controlar dieta")

    # Crear examen legacy
    admin_manager.crear_resultado_examen("EXLEG001", {
        "documento_paciente": documento,
        "paciente": "Paciente X",
        "codigo_cita": "CITA999",
        "examen_solicitado": "Hemograma",
        "medico": {"documento": "M001"},
        "diagnostico": "Anemia leve",
        "estado": "pendiente"
    })

    ex_list = service.obtener_examenes_paciente(documento)
    codigos = {e["codigo"] for e in ex_list}
    assert "EXLEG001" in codigos
    assert resultado["id"] in codigos
    # Verificar origenes
    origenes = {e["origen"] for e in ex_list}
    assert "legacy" in origenes and "workflow" in origenes

    # Ver resultado individual workflow
    detalle = service.obtener_resultado_examen(resultado["id"])
    assert detalle["id"] == resultado["id"]

    # Ver resultado individual legacy
    detalle_leg = service.obtener_resultado_examen("EXLEG001")
    assert detalle_leg["codigo_examen"] == "EXLEG001"

    shutil.rmtree(base)
