import pytest
from app.managers.cita_manager import CitaManager

def test_agendar_cita_exito():
    cm = CitaManager()
    assert cm.agendar_cita("Juan", "Dr. Pérez", "2025-04-10")

def test_cita_duplicada():
    cm = CitaManager()
    cm.agendar_cita("Juan", "Dr. Pérez", "2025-04-10")
    with pytest.raises(ValueError):
        cm.agendar_cita("Juan", "Dr. Pérez", "2025-04-10")
