# Explicación Detallada del Flujo de Datos y Persistencia

Esta documentación describe cómo se crean y transforman los objetos principales del sistema (Pacientes, Médicos, Citas, Diagnósticos, Solicitudes y Resultados de Exámenes, Exámenes Legacy) y cómo interactúan los roles (Paciente, Médico, Administrador) a través de los endpoints. Es coherente con el diagrama `casos_uso_detallado.mmd`.

## 1. Visión General de Roles
- **Paciente**: Puede registrarse, autenticarse (JWT), crear y eliminar citas propias, listar sus citas y consultar exámenes (fusionados legacy + workflow).
- **Médico**: Se registra, autentica y puede ver su agenda sincronizada, cerrar citas (generando diagnósticos y solicitudes de exámenes).
- **Administrador**: Único usuario definido por variables de entorno (`ADMIN_USERNAME`, `ADMIN_SECRET_KEY`); autoriza solicitudes y registra resultados de exámenes.

## 2. Seguridad y Control de Acceso
- Los tokens JWT se generan en `PacienteService.login_paciente`, `MedicoService.login_medico` y `AdminService.login_admin`.
- El módulo `roles.py` provee dependencias `require_role` y `get_payload` para restringir endpoints por tipo de usuario.
- Validación adicional por documento (paciente) asegura que no pueda acceder a datos ajenos.

## 3. Persistencia Base
Carpeta base (por defecto): `~/memoryApps/saludVital/`
Estructura clave:
- `pacientes/{documento}.json`: Datos de paciente.
- `medicos/{documento_medico}.json`: Datos de médico + citas atendidas.
- `citas/{documento_paciente}.json`: Citas por paciente.
- `agendas/{documento_medico}.json`: Agenda consolidada del médico.
- `diagnosticos/{codigo_cita}.json`: Diagnóstico de una cita realizada.
- `examenes_solicitudes.json`: Todas las solicitudes de exámenes (workflow).
- `examenes_resultados.json`: Resultados asociados a solicitudes autorizadas.
- `examenes/{codigo_examen}.json`: Exámenes legacy (creados por método antiguo).
- `admins/` (sin uso en modo actual de admin único por entorno).

## 4. Flujo de Creación de Objetos
### 4.1 Paciente
1. `POST /pacientes/registro` -> `PacienteService.registrar_paciente` -> `PacienteManager.registrar_paciente`.
2. Se crea JSON con campos: documento, nombre, hash(contraseña), teléfono, email, edad, sexo, fecha registro.
3. Login genera token con: `{ documento, nombre_completo, tipo_usuario: paciente, exp }`.

### 4.2 Médico
1. `POST /medicos/registro` -> `MedicoService.registrar_medico` -> `MedicoManager.registrar_medico`.
2. Archivo JSON incluye: documento, nombre, hash(contraseña), teléfono, email, especialidad, citas_atendidas[].
3. Login genera token con `{ documento, nombre_completo, tipo_usuario: medico, exp }`.

### 4.3 Cita
1. `POST /citas` (paciente) -> `CitaManager.agendar_cita`.
2. Validación de fecha: `_verificar_fecha` soporta naive y con zona horaria (Z / +00:00). Convierte para comparación segura.
3. Se guarda en `citas/{documento_paciente}.json` y duplica en `agendas/{documento_medico}.json`.
4. Campos de la cita: paciente, medico (string), medico_info (doc/nombre), fecha (original), documento (paciente), registrado (ISO), codigo_cita (6 chars), tipoCita, motivoPaciente, prioridad.

### 4.4 Agenda del Médico
- Se actualiza inmediatamente al crear cita.
- Consulta mediante `GET /medicos/agenda` normaliza fechas para evitar errores naive vs aware.

### 4.5 Cierre de Cita y Diagnóstico
1. `POST /medicos/cerrar-cita` -> `MedicoService.cerrar_cita`.
2. Valida estado (`realizada`, `cancelada`, `noAsistida`). Si `realizada` y se incluye `diagnostico`:
   - Se agrega información del médico al dict.
   - Se persiste el diagnóstico en `diagnosticos/{codigo_cita}.json` (normalización de cualquier datetime presente).
   - Se marca cita atendida en el archivo del médico (citas_atendidas).
   - Si hay `examenes_solicitados`, se crea una solicitud por examen mediante `ExamenWorkflowService.crear_solicitud`.

### 4.6 Solicitudes de Examen (Workflow)
1. Creación: `crear_solicitud(codigo_cita, documento_paciente, documento_medico, tipo_examen)` -> añade entrada a `examenes_solicitudes.json` con estado inicial `solicitado`.
2. Autorización: `POST /examenes/solicitudes/autorizar` -> update estado a `autorizado` con timestamp `fecha_autorizacion`.
3. Registro de resultado: `POST /examenes/resultados` -> crea entrada en `examenes_resultados.json` y actualiza solicitud a estado `resultado` (+ `fecha_resultado`).
4. Evaluación de riesgo simple: valores >180 => crítico; >140 => alerta; else normal.

### 4.7 Exámenes Legacy
- Persistidos con `AdminManager.crear_resultado_examen` en `examenes/{codigo_examen}.json`.
- Estado inicial: `pendiente`.
- Uso previsto: compatibilidad histórica; se migrará a workflow.

### 4.8 Fusión de Exámenes para Paciente
1. `GET /pacientes/examenes` -> `PacienteService.obtener_examenes_paciente`.
2. Obtiene lista legacy y resultados workflow.
3. Normaliza estructura común:
   - `codigo`: id (workflow) o codigo_examen (legacy).
   - `tipo_examen`: disponible solo en legacy (workflow requiere solicitarlo desde la solicitud original; actualmente null).
   - `origen`: `legacy` | `workflow`.
   - `estado_riesgo`: solo workflow.
   - `interpretacion`: workflow usa campo; legacy reutiliza diagnóstico.
4. Retorno combinado permite transición gradual sin pérdida de visibilidad.

## 5. Serialización y Normalización
- Fechas: se transforman para comparar (agenda y verificación de cita) y se conservan en formato original ISO para mantener compatibilidad con tests.
- Datetimes en diagnósticos y repositorios: convertidos a ISO usando `.isoformat()` antes de `json.dump`.
- Repositorios (`BaseRepository`) incluyen un `default` para serializar objetos datetime.

## 6. Casos de Uso Principales (diagramados)
1. Paciente agenda cita -> cita sincronizada a agenda médico.
2. Médico cierra cita con diagnóstico y solicita exámenes -> solicitudes en `examenes_solicitudes.json`.
3. Administrador autoriza y registra resultados -> resultado en `examenes_resultados.json` + actualización del estado de la solicitud.
4. Paciente consulta exámenes -> fusión de legacy y workflow.

## 7. Consideraciones de Seguridad
- No existe endpoint público para crear administradores (único admin por entorno).
- Paciente solo ve sus citas y exámenes (control por documento + rol).
- Médico no puede acceder a citas de otros pacientes (control por documento y agenda propia).
- Acceso a autorización y registro de exámenes restringido a rol admin.

## 8. Limitaciones y Mejoras Potenciales
- `tipo_examen` no se rellena en resultados workflow; se puede recuperar desde la solicitud correspondiente.
- No hay endpoint para listar solicitudes de exámenes por paciente/médico (solo resultados). Agregarlo facilitaría la UI.
- Exámenes legacy deberían migrarse a workflow (script de migración sugerido: leer archivos en `examenes/` y crear solicitudes + resultados).
- Falta auditoría de acciones (quién autorizó, cuándo) más allá de timestamps.
- Hash de contraseñas del médico/paciente usa SHA-256 sin salt; recomendable migrar a bcrypt/argon2.

## 9. Flujo Resumido End-to-End
1. Paciente se registra y agenda cita.
2. Cita persiste en dos lugares: archivo del paciente y agenda del médico.
3. Médico cierra cita y solicita exámenes -> crea solicitud (estado `solicitado`).
4. Administrador autoriza solicitud -> estado `autorizado`.
5. Administrador registra resultado -> estado solicitud `resultado`, resultado persistido con riesgo calculado.
6. Paciente consulta exámenes -> ve legado (si existiera) + workflow.

## 10. Referencias Cruzadas
- Diagrama: `casos_uso_detallado.mmd` (estructura de nodos y archivos).
- Código clave: `CitaManager`, `MedicoService`, `ExamenWorkflowService`, `PacienteService`, `AdminService`, `roles.py`.

---
**Fin de la explicación técnica detallada.**

