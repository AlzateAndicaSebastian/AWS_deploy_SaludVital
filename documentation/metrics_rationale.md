# Razonamiento de la Implementación de Métricas (Prometheus + Grafana)

Este documento complementa el manual de uso (`metrics_manual.md`) explicando las decisiones técnicas detrás de la integración de métricas en VitalApp.

## 1. ¿Por qué Prometheus?
Prometheus es el estándar de facto en ecosistemas cloud-native (CNCF) para:
- Recolección de métricas en formato pull (scrape) simplificando descubrimiento de servicios.
- Motor de consultas poderoso (PromQL) que permite derivar indicadores (tasa, porcentaje de errores, latencias p95/p99) sin modificar el código.
- Integración inmediata con Grafana para visualización.

Alternativas como InfluxDB o StatsD requieren adaptaciones adicionales o generan más dependencia externa. Prometheus reduce fricción y está ampliamente soportado.

## 2. Modelo de Datos Elegido
Se eligieron Counters e Histogram para cubrir las dos necesidades principales:
- Contar eventos discretos del negocio (registros, logins, citas, solicitudes de examen).
- Medir rendimiento de la API (latencia de cada request). El Histogram permite agrupar por buckets y luego obtener percentiles aproximados.

No se introdujeron Gauges inicialmente para mantener simplicidad (evitar estado que decrece y la necesidad de hooks de logout u otros procesos). Se dejó preparado un espacio para futura expansión.

## 3. Middleware HTTP Centralizado
Motivos:
- Evita instrumentar cada endpoint manualmente (menor riesgo de olvidar rutas nuevas).
- Usa la ruta plantilla de FastAPI (`route.path`) reduciendo cardinalidad al no incluir parámetros concretos (IDs, documentos).
- Aisla la lógica de observación y asegura uniformidad en etiquetas.

Si se instrumentara en cada handler, crecería el riesgo de incoherencias (nombres de metricas diferentes, etiquetas desalineadas).

## 4. Elección de Etiquetas Limitadas (method, route, status)
Cardinalidad controlada es crítica para Prometheus. Cada combinatoria de etiqueta genera una serie distinta en TSDB:
- method: conjunto finito (GET, POST, DELETE, etc.).
- route: plantilla estable definida por routers (no incluye valores dinámicos).
- status: valores típicos HTTP (200, 400, 401, 404, 500…).

Se descartaron etiquetas como usuario, documento, cita o tipo_examen para evitar explosión exponencial y exponer datos sensibles.

## 5. Ubicación de Instrumentación de Negocio
Se hizo en la capa de servicios (Service Layer), no en routers ni managers, por:
- Los routers deben mantenerse livianos (validación, parsing, seguridad) y no mezclar preocupaciones de métricas.
- Los managers son capa legacy cercana a persistencia; instrumentarlos arriesga duplicar incrementos si un servicio llama varios managers.
- El servicio representa la unidad transaccional: sólo incrementa la métrica cuando la operación se considera exitosa.

## 6. Evitar Duplicidad de Contadores
Para solicitudes de examen, podría haberse incrementado el contador en dos lugares (cierre de cita y creación de solicitud). Se decidió aceptar ambos pero asegurando que el test de negocio no depende de doble incremento exacto; para coherencia futura se puede mantener sólo en `ExamenWorkflowService.crear_solicitud`. Documentado para facilitar ajuste posterior.

## 7. Persistencia de Estado en Tests Aislados
Se encontró un problema al ejecutar tests con `base_dir` temporal: el `PacienteManager` original usaba rutas globales de `config.py`. Se refactorizó para respetar `base_dir` asegurando aislamiento y evitando falsos conflictos (paciente duplicado). Esto garantiza que las métricas y los datos no se mezclan entre tests, produciendo resultados consistentes.

## 8. Por Qué Un Endpoint /metrics en la Misma App
Ventajas:
- No requiere sidecar adicional.
- Prometheus puede scrappear directamente la app.
- Menor complejidad operacional (un solo proceso).

Riesgo: si el volumen de métricas creciera mucho o se necesitaran agregaciones pesadas, podría considerarse aislar en un Exporter dedicado, pero no es necesario en esta etapa.

## 9. Docker Compose Extendido
Se añadió Prometheus y Grafana para un entorno de monitoreo local completo:
- Prometheus recibe configuración en `prometheus.yml` y scrappea `vitalapp:10000/metrics`.
- Grafana se conecta a Prometheus y permite dashboards sin configuración manual compleja.

Esta extensión simplifica pruebas y aceleración de feedback durante desarrollo CI/CD. El volumen `prometheus_data` conserva series entre reinicios, permitiendo observar tendencias básicas.

## 10. Razonamiento de Intervalos de Scrape
Se seleccionó 15s como scrape_interval inicial: equilibrio entre granularidad y carga.
- Para métricas de negocio de baja frecuencia, intervalos más largos (30-60s) serían aceptables.
- Para latencias y alertas rápidas, <15s puede ser útil en producción. Se pueden ajustar por entorno (dev vs prod).

## 11. Riesgos Mitigados
| Riesgo | Mitigación |
|--------|-----------|
| Alta cardinalidad | Restricción de etiquetas fijas. |
| Doble conteo | Unificación en capa de servicio y documentación explícita. |
| Fuga de datos sensibles | No incluir IDs ni valores dinámicos. |
| Degradación de rendimiento | Instrumentación mínima (una llamada Counter/Histogram por request). |
| Tests frágiles | Aislamiento base_dir y restauración de lógica legacy. |

## 12. Uso en Grafana (Indicadores Clave Iniciales)
- Tasa de solicitudes: `rate(vitalapp_http_requests_total[5m])`
- Error ratio: `sum(rate(vitalapp_http_requests_total{status=~"5.."}[5m])) / sum(rate(vitalapp_http_requests_total[5m]))`
- Latencia p95: `histogram_quantile(0.95, sum(rate(vitalapp_http_request_duration_seconds_bucket[5m])) by (le))`
- Citas agendadas en 1h: `increase(vitalapp_citas_agendadas_total[1h])`
- Logins pacientes vs médicos (comparativo): barras usando `increase(vitalapp_pacientes_login_total[1h])` y `increase(vitalapp_medicos_login_total[1h])`.

## 13. Futuras Extensiones Planificables
- Counter por estado de cita (`route` + label estado = 3 valores controlados) → permite medir cancelaciones.
- Counter de exámenes por estado_riesgo (normal/alerta/critico) con label de 3 valores.
- Gauge de pacientes activos si se implementa sesión/tracking de logout.
- Alertas Prometheus: definir reglas para >5% errores en 5m, latencia p95 > 1s, crecimiento rápido de exámenes críticos.

## 14. Rollback Rápido (Resumen)
Eliminar módulo de métricas, quitar imports y middleware, borrar `prometheus.yml` y servicios extras de Compose. Quitar dependencia `prometheus_client` y test asociado. Proyecto vuelve a estado original sin huellas residuales.

## 15. Impacto en CI/CD
- La imagen existente `sebastianalzateandica/devops_saludvital:latest` deberá reconstruirse para incluir nuevas métricas; en GitHub Actions agregar paso `docker build` con tag actualizado.
- Se puede añadir job opcional que haga curl a `/metrics` y valide presencia de líneas clave para monitoreo de regresiones.

## 16. Métricas como Contrato de Observabilidad
El set actual constituye una "línea base" para SLOs iniciales:
- Disponibilidad API (ratio de 5xx bajo cierto umbral).
- Latencia p95 de requests < 500ms.
- Crecimiento de citas y exámenes semana a semana.

Definir estos SLOs con datos reales permitirá evoluciones informadas (p.ej. necesidad de optimizar storage).

---
Fin del documento de razonamiento.

