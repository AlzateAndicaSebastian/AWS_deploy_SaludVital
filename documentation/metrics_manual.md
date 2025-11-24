# Manual de Métricas Prometheus - VitalApp

Este manual describe la integración de métricas Prometheus en VitalApp y explica cómo añadir nuevas métricas siguiendo las convenciones adoptadas.

## 1. Objetivos
- Exponer métricas HTTP (latencia y conteo de solicitudes) para monitoreo de rendimiento.
- Capturar eventos clave del negocio: registros y logins de usuarios, citas agendadas, solicitudes de exámenes.
- Facilitar la futura visualización en Grafana sin alta cardinalidad.

## 2. Arquitectura de Integración
```
FastAPI Middleware -> métricas HTTP
Servicios de negocio -> helpers de métricas de negocio
/metrics -> endpoint Prometheus (texto plano)
Prometheus Server (externo) -> scrape /metrics
Grafana -> consume Prometheus para dashboards
```

## 3. Convenciones de Nombres
- Prefijo `vitalapp_` para todas las métricas.
- Usar snake_case descriptivo claro: `vitalapp_http_requests_total`, `vitalapp_pacientes_registrados_total`.
- Sufijos comunes:
  - `_total` para Counters.
  - `_seconds` para Histogram de duración.

## 4. Tipos de Métricas Utilizados
| Tipo | Uso | Ejemplo |
|------|-----|---------|
| Counter | Eventos que solo aumentan | `vitalapp_citas_agendadas_total` |
| Histogram | Distribución de duraciones | `vitalapp_http_request_duration_seconds` |
| Gauge (futuro) | Valores que suben/bajan | `vitalapp_pacientes_activos` (no implementado aún) |

### ¿Por qué Counter para eventos?
Counters permiten cálculos de tasas (rate) en Prometheus y son inmutables (solo crecen o se reinician al reiniciar el proceso).

## 5. Métricas Actuales
- HTTP:
  - `vitalapp_http_requests_total{method,route,status}`
  - `vitalapp_http_request_duration_seconds_bucket{method,route,le}` y sum/count
- Negocio:
  - `vitalapp_citas_agendadas_total`
  - `vitalapp_examenes_solicitudes_total`
  - `vitalapp_pacientes_registrados_total`
  - `vitalapp_medicos_registrados_total`
  - `vitalapp_pacientes_login_total`
  - `vitalapp_medicos_login_total`

## 6. Etiquetas (Labels)
Solo se utilizan: `method`, `route`, `status` (HTTP). Esto asegura baja cardinalidad.

### Buenas Prácticas de Etiquetas
- NO usar IDs de usuarios, códigos de cita o correos electrónicos.
- NO introducir etiquetas con valores potencialmente ilimitados.
- Mantener rutas normalizadas (FastAPI provee plantilla: `/citas/{documento}`) evitando valores reales dinámicos.

## 7. Flujo de Instrumentación
1. Middleware captura cada solicitud:
   - Incrementa `vitalapp_http_requests_total`.
   - Observa latencia en `vitalapp_http_request_duration_seconds`.
2. Servicios de negocio llaman helpers al completar eventos:
   - Registro paciente → `inc_paciente_registrado()`.
   - Login médico → `inc_medico_login()`.
   - Crear cita → `inc_cita_agendada()`.
   - Crear solicitud examen → `inc_examen_solicitado()`.

## 8. Archivo Central de Métricas
Ubicación: `app/metrics/metrics.py`
Contiene:
- Definiciones de métricas.
- Helpers para incrementar contadores.
- Función `observe_request()` para el middleware.
- Exportación de `generate_latest` y `CONTENT_TYPE_LATEST`.

## 9. Cómo Añadir una Nueva Métrica
Supongamos que queremos medir el número de citas canceladas.

### Paso 1: Definir la métrica en `metrics.py`
```python
from prometheus_client import Counter
CITAS_CANCELADAS_TOTAL = Counter(
    'vitalapp_citas_canceladas_total',
    'Total de citas canceladas'
)

def inc_cita_cancelada():
    CITAS_CANCELADAS_TOTAL.inc()
```
Añadir `inc_cita_cancelada` a `__all__` si se expone.

### Paso 2: Instrumentar el punto de negocio
En el servicio que procesa cancelaciones (ej. `MedicoService.cerrar_cita` si estado=="cancelada"):
```python
from app.metrics.metrics import inc_cita_cancelada
# dentro de la lógica donde se confirma cancelación
if estado == 'cancelada':
    inc_cita_cancelada()
```

### Paso 3: (Opcional) Añadir test
Crear o editar `tests/test_metrics.py` para provocar una cancelación y luego verificar presencia de la métrica:
```python
assert 'vitalapp_citas_canceladas_total' in metrics_text
```

### Paso 4: Documentar el cambio
Actualizar este manual añadiendo la métrica a la sección de Métricas Actuales si es estable.

## 10. Añadir un Histogram o Gauge Nuevo
Ejemplo Gauge para pacientes activos (incremento al login, decremento al logout futuro):
```python
from prometheus_client import Gauge
PACIENTES_ACTIVOS = Gauge('vitalapp_pacientes_activos', 'Pacientes con sesión activa')

# Al login exitoso
PACIENTES_ACTIVOS.inc()
# Al logout (cuando se implemente)
PACIENTES_ACTIVOS.dec()
```

Histogram personalizado (ej. tiempo de autorización de examen):
```python
from prometheus_client import Histogram
EXAMEN_AUTORIZACION_DURATION_SECONDS = Histogram(
    'vitalapp_examen_autorizacion_duration_seconds',
    'Tiempo para autorizar una solicitud de examen',
    buckets=[0.1,0.3,0.5,1,2,5]
)

start = time.perf_counter()
# ...autorizar...
EXAMEN_AUTORIZACION_DURATION_SECONDS.observe(time.perf_counter() - start)
```

## 11. Verificación Rápida
Levantar el servicio y hacer:
```bash
curl -s http://localhost:10000/metrics | grep vitalapp_http_requests_total
```
Debe aparecer líneas similares a:
```
vitalapp_http_requests_total{method="GET",route="/",status="200"} 1.0
```

## 12. Prometheus Scrape Config (Ejemplo)
En `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'vitalapp'
    scrape_interval: 15s
    static_configs:
      - targets: ['vitalapp-service:10000']
```

## 13. Consideraciones de Cardinalidad
- Limitar rutas para evitar explosión de series.
- No utilizar etiquetas basadas en datos del usuario.
- Revisar periódicamente número de series (`curl /metrics | wc -l`).

## 14. Rendimiento
- `prometheus_client` maneja concurrencia interna; Counters e Histograms son seguros.
- Evitar instrumentar bucles muy intensivos sin necesidad.

## 15. Rollback Sencillo
1. Eliminar `app/metrics/metrics.py`.
2. Quitar imports y middleware de `app/main.py`.
3. Remover imports y llamadas a helpers en servicios.
4. Eliminar `prometheus_client` de `requirements.txt` y reinstalar dependencias.
5. Borrar tests/documentación asociada.

## 16. Testing de Métricas
Test recomendado (simplificado):
```python
from fastapi.testclient import TestClient
from app.main import app

def test_metricas_basicas():
    client = TestClient(app)
    r = client.get('/')
    assert r.status_code == 200
    m = client.get('/metrics')
    text = m.text
    assert 'vitalapp_http_requests_total' in text
```

## 17. Futuras Extensiones
- Métricas de riesgo de examen por estado (`critico`, `alerta`, `normal`) usando Counter con label estado (controlado).
- Métricas de citas por estado (realizada/cancelada/noAsistida) con label fijo para 3 estados.
- Summary para percentiles de latencia si se requiere (no imprescindible con Histogram + Prometheus).

## 18. Checklist al Añadir Métrica
1. ¿El nombre sigue prefijo y convención? Sí.
2. ¿El tipo es apropiado (Counter vs Gauge vs Histogram)? Sí.
3. ¿Evita alta cardinalidad? Sí.
4. ¿Instrumentación coloca la llamada tras confirmar éxito? Sí.
5. ¿Test actualizado? Sí.
6. ¿Documentado? Sí.

## 19. Preguntas Frecuentes
- ¿Necesito reiniciar el servicio al añadir una métrica? Sí, se registran al iniciar.
- ¿Qué ocurre si repito un nombre con distintas etiquetas? Dará error en registro inicial.
- ¿Puedo borrar una métrica sin reiniciar? No, requiere reinicio del proceso.

---
Fin del manual.

