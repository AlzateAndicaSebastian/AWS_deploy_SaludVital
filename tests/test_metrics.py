from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def _registrar_paciente(documento: str):
    return client.post('/pacientes/registro', json={
        "documento": documento,
        "nombre_completo": "Paciente Test",
        "contraseña": "secret",
        "telefono": "123",
        "email": f"{documento}@test.local",
        "edad": 30,
        "sexo": "M"
    })

def _login_paciente(documento: str):
    return client.post('/pacientes/login', json={
        "documento": documento,
        "contraseña": "secret"
    })

def _registrar_medico(documento: str):
    return client.post('/medicos/registro', json={
        "documento": documento,
        "nombre_completo": "Medico Test",
        "contraseña": "secret",
        "telefono": "999",
        "email": f"{documento}@med.local",
        "especialidad": "General"
    })

def _login_medico(documento: str):
    return client.post('/medicos/login', json={
        "documento": documento,
        "contraseña": "secret"
    })

def _crear_cita(token: str, documento_paciente: str):
    return client.post('/citas/', json={
        "paciente": "Paciente Test",
        "medico": "Medico Test",
        "fecha": "2030-01-01T10:00:00",
        "documento": documento_paciente,
        "tipoCita": "general",
        "motivoPaciente": "control"
    }, headers={"Authorization": f"Bearer {token}"})


def test_metricas_negocio_y_http():
    doc_pac = str(uuid.uuid4())[:8]
    doc_med = str(uuid.uuid4())[:8]

    # Registro paciente
    r1 = _registrar_paciente(doc_pac)
    assert r1.status_code == 201
    # Login paciente
    r2 = _login_paciente(doc_pac)
    assert r2.status_code == 200
    token_pac = r2.json().get('token')

    # Registro medico
    r3 = _registrar_medico(doc_med)
    assert r3.status_code == 201
    # Login medico
    r4 = _login_medico(doc_med)
    assert r4.status_code == 200

    # Crear cita
    r5 = _crear_cita(token_pac, doc_pac)
    assert r5.status_code == 200

    # Obtener métricas
    metrics = client.get('/metrics')
    assert metrics.status_code == 200
    text = metrics.text

    # Validaciones de presencia
    assert 'vitalapp_pacientes_registrados_total' in text
    assert 'vitalapp_pacientes_login_total' in text
    assert 'vitalapp_medicos_registrados_total' in text
    assert 'vitalapp_medicos_login_total' in text
    assert 'vitalapp_citas_agendadas_total' in text
    assert 'vitalapp_http_requests_total' in text

    # Opcional: verificar que los contadores sean >=1
    # Buscamos línea del contador de pacientes registrados
    lines = [l for l in text.split('\n') if 'vitalapp_pacientes_registrados_total' in l and '#' not in l]
    assert any(float(l.split()[-1]) >= 1 for l in lines)

