# Guía de Interpretación del Dashboard Grafana - VitalApp

Este documento explica cada panel del dashboard simplificado y el significado de las métricas usadas.

## 1. Conceptos Básicos
- Ventana (5m): Muchas métricas usan `rate(...[5m])` que calcula la velocidad promedio del contador en los últimos 5 minutos.
- Counter: Métrica que solo incrementa (ej. `*_total`). Para tasas se usa `rate()` o `increase()`.
- Histogram: Métrica con sufijos `_bucket`, `_sum`, `_count` que permite estimar percentiles (p95) y promedio.
- Percentil p95: Valor bajo el cual el 95% de las observaciones ocurren; muestra experiencia típica evitando picos extremos.

## 2. Métricas Disponibles
| Métrica | Tipo | Descripción |
|--------|------|-------------|
| vitalapp_http_requests_total | Counter con labels (method, route, status) | Conteo de solicitudes HTTP procesadas. |
| vitalapp_http_request_duration_seconds_bucket/sum/count | Histogram | Distribución y suma de latencias por bucket. |
| vitalapp_citas_agendadas_total | Counter | Citas creadas. |
| vitalapp_examenes_solicitudes_total | Counter | Solicitudes de examen generadas. |
| vitalapp_pacientes_registrados_total | Counter | Pacientes registrados. |
| vitalapp_medicos_registrados_total | Counter | Médicos registrados. |
| vitalapp_pacientes_login_total | Counter | Logins exitosos de pacientes. |
| vitalapp_medicos_login_total | Counter | Logins exitosos de médicos. |

## 3. Paneles y Significado
### Throughput HTTP (req/s últimos 5m)
- Query: `sum(rate(vitalapp_http_requests_total[5m]))`
- Mide la carga actual (solicitudes por segundo). Un aumento sostenido puede requerir escalado.

### Porcentaje de Errores 5xx
- Query: `(sum(rate(vitalapp_http_requests_total{status=~"5.."}[5m])) / sum(rate(vitalapp_http_requests_total[5m]))) * 100`
- Indica estabilidad interna. > 5% es señal para investigar (logs, saturación, excepciones).

### Latencia p95 (últimos 5m)
- Query: `histogram_quantile(0.95, sum(rate(vitalapp_http_request_duration_seconds_bucket[5m])) by (le))`
- Tiempo que cubre al 95% de las solicitudes. Si crece junto a throughput, posible saturación.

### Distribución de Latencias (Buckets)
- Query: `sum(rate(vitalapp_http_request_duration_seconds_bucket[5m])) by (le)`
- Muestra cuántas solicitudes caen por debajo de cada límite de bucket. Permite ver si aparecen muchas en buckets altos.

### Solicitudes por Ruta (Top 8)
- Query: `topk(8, sum(rate(vitalapp_http_requests_total{route=~"$route"}[5m])) by (route))`
- Rutas más activas. Prioriza optimización/cache en estas.

### Errores Cliente vs Servidor
- Queries: sum de 4xx y 5xx.
- Distingue problemas de validación (4xx) de fallos internos (5xx). Si predominan 4xx, mejorar UX/validaciones.

### Logins por Tipo de Usuario
- Queries: `rate(vitalapp_pacientes_login_total[5m])` y `rate(vitalapp_medicos_login_total[5m])`
- Actividad reciente de autenticación. Picos inesperados pueden ser reintentos por error.

### Usuarios Registrados (Acumulado)
- Counters directos.
- Mide crecimiento de base instalada. Curvas planas pueden indicar estancamiento comercial.

### Engagement Pacientes / Médicos (%)
- `rate(login_total[5m]) / clamp_min(registrados_total,1) * 100`
- Porcentaje de usuarios que inician sesión en ventana vs total. Útil para adopción.

### Clases de Código HTTP
- Tasa de 2xx (éxito), 4xx (error de cliente), 5xx (error servidor).
- Cambios en proporción ayudan a detectar degradación.

### Citas vs Solicitudes de Exámenes (Incremento Hora)
- Queries: `increase(vitalapp_citas_agendadas_total[1h])` y `increase(vitalapp_examenes_solicitudes_total[1h])`
- Volumen de actividad clínica. Divergencia puede indicar patrón (más exámenes por cita, etc.).

### Rutas con Mayor Latencia Media
- Query: `topk(10, (sum(rate(..._sum[5m])) / sum(rate(..._count[5m]))) )`
- Rutas más lentas promedio. Revisar código/IO externo en esas.

### Latencia Media Estimada (5m)
- Promedio simple: sum(rate(sum)) / sum(rate(count)). Muestra tendencia general complementaria a p95.

### Total Citas Agendadas / Total Solicitudes de Exámenes
- Counters acumulados. Ver tendencia larga (selecciona rango mayor en Grafana).

### Ratio Exámenes por Cita (%)
- `examenes_total / citas_total * 100`
- Indica intensidad diagnóstica por cita. Cambios súbitos pueden señalar cambios en protocolos médicos.

## 4. Umbrales Orientativos (No son Alertas Automáticas)
| Métrica | Umbral sugerido | Acción |
|---------|-----------------|--------|
| Error 5xx % > 5% | Revisar logs y saturación | Escalar, perfilado |
| Latencia p95 > 0.5s | Revisar endpoints lentos | Optimizar consultas |
| Engagement Pacientes < 5% (picos bajos) | Posible baja adopción | Revisar flujo de login |
| Ratio Exámenes/Cita > 200% | Posible exceso de solicitudes | Auditar lógica de solicitud |

## 5. Buenas Prácticas de Lectura
1. Comienza por Throughput y Errores 5xx (salud general).
2. Revisa Latencia p95 y Media (rendimiento). Si p95 >> media, hay colas o picos.
3. Verifica si rutas más activas coinciden con las más lentas (acción prioritaria).
4. Observa Engagement para analítica de uso real.
5. Ajusta el rango temporal (arriba a la derecha) para ver tendencias (24h, 7d).

## 6. Cómo Crear Alertas Modernas (Resumen)
- En un panel timeseries (ej. Error 5xx), botón "Alert" -> "Create rule".
- Condición: `sum(rate(vitalapp_http_requests_total{status=~"5.."}[5m])) / sum(rate(vitalapp_http_requests_total[5m])) * 100 > 5` por 5m.
- Notificación: canal (email/Slack).

## 7. Problemas Comunes
| Problema | Causa | Solución |
|----------|-------|----------|
| Panel vacío | Falta de tráfico | Realizar solicitudes a la API |
| Todos valores cero | Servicio recién reiniciado | Esperar ventana rate (hasta 5 min) |
| Histogram sin buckets | Instrumentación faltante | Verificar middleware y métricas expuestas |

## 8. Extensiones Futuras
- Añadir métricas de estado de citas (realizada/cancelada) con label controlado.
- Métricas de riesgo de exámenes (criticidad) para panel clínico.
- Dashboard separado para rendimiento vs negocio.

## 9. Referencia Rápida de Consultas
- p95: `histogram_quantile(0.95, sum(rate(vitalapp_http_request_duration_seconds_bucket[5m])) by (le))`
- Latencia media: `sum(rate(vitalapp_http_request_duration_seconds_sum[5m])) / sum(rate(vitalapp_http_request_duration_seconds_count[5m]))`
- Throughput: `sum(rate(vitalapp_http_requests_total[5m]))`
- Error ratio: `(sum(rate(vitalapp_http_requests_total{status=~"5.."}[5m])) / sum(rate(vitalapp_http_requests_total[5m]))) * 100`

## 10. Checklist de Interpretación Diaria
1. Error 5xx < 5% ✅
2. p95 estable (<0.5s) ✅
3. Throughput dentro de lo esperado ✅
4. Latencia media y p95 alineadas (sin cola) ✅
5. Engagement > 5% ✅
6. Ratio Exámenes/Cita razonable (<150%) ✅

---
Fin de la guía.

