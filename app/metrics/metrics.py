"""Módulo central de métricas Prometheus para VitalApp.
Convenciones:
- Prefijo vitalapp_ para todas las métricas.
- Etiquetas controladas (baja cardinalidad) únicamente: method, route, status.
- No incluir identificadores sensibles (documentos, emails, códigos dinámicos).

Helpers expuestos para incrementar métricas de negocio desde servicios.
"""
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from time import perf_counter

# Métricas HTTP
HTTP_REQUESTS_TOTAL = Counter(
    'vitalapp_http_requests_total',
    'Conteo de solicitudes HTTP procesadas',
    ['method', 'route', 'status']
)
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    'vitalapp_http_request_duration_seconds',
    'Duración de solicitudes HTTP (segundos)',
    ['method', 'route']
)

# Métricas de negocio
CITAS_AGENDADAS_TOTAL = Counter(
    'vitalapp_citas_agendadas_total',
    'Total de citas agendadas'
)
EXAMENES_SOLICITUDES_TOTAL = Counter(
    'vitalapp_examenes_solicitudes_total',
    'Total de solicitudes de exámenes creadas'
)
PACIENTES_REGISTRADOS_TOTAL = Counter(
    'vitalapp_pacientes_registrados_total',
    'Total de pacientes registrados'
)
MEDICOS_REGISTRADOS_TOTAL = Counter(
    'vitalapp_medicos_registrados_total',
    'Total de médicos registrados'
)
PACIENTES_LOGIN_TOTAL = Counter(
    'vitalapp_pacientes_login_total',
    'Total de logins exitosos de pacientes'
)
MEDICOS_LOGIN_TOTAL = Counter(
    'vitalapp_medicos_login_total',
    'Total de logins exitosos de médicos'
)

# Futuras métricas (ejemplo gauge) podrían declararse aquí.
# from prometheus_client import Gauge
# PACIENTES_ACTIVOS = Gauge('vitalapp_pacientes_activos', 'Pacientes con sesión activa')

# Helpers negocio

def inc_cita_agendada():
    CITAS_AGENDADAS_TOTAL.inc()

def inc_examen_solicitado():
    EXAMENES_SOLICITUDES_TOTAL.inc()

def inc_paciente_registrado():
    PACIENTES_REGISTRADOS_TOTAL.inc()

def inc_medico_registrado():
    MEDICOS_REGISTRADOS_TOTAL.inc()

def inc_paciente_login():
    PACIENTES_LOGIN_TOTAL.inc()

def inc_medico_login():
    MEDICOS_LOGIN_TOTAL.inc()

# Helpers HTTP (usado por middleware)

def observe_request(method: str, route: str, status: int, duration_seconds: float):
    # Normalización defensiva
    method = (method or 'UNKNOWN').upper()
    route = route or 'unknown'
    status_str = str(status)
    HTTP_REQUESTS_TOTAL.labels(method=method, route=route, status=status_str).inc()
    HTTP_REQUEST_DURATION_SECONDS.labels(method=method, route=route).observe(duration_seconds)

# Endpoint /metrics usará generate_latest() y CONTENT_TYPE_LATEST
__all__ = [
    'generate_latest', 'CONTENT_TYPE_LATEST',
    'inc_cita_agendada', 'inc_examen_solicitado', 'inc_paciente_registrado',
    'inc_medico_registrado', 'inc_paciente_login', 'inc_medico_login',
    'observe_request'
]

