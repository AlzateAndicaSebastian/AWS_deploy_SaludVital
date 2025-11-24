from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from app.managers.cita_manager import CitaManager
from app.managers.historial_cita import HistorialCita
from app.managers.resultados import Resultados
from app.managers.alertas import Alertas
from app.routers.citas_router import router as citas_router
from app.routers.paciente_router import router as paciente_router
from app.routers.medico_router import router as medico_router
from app.routers.admin_router import router as admin_router
from app.routers.examenes_router import router as examenes_router
# Métricas
from app.metrics.metrics import observe_request, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import time

app = FastAPI(title="VitalApp API")

# Cargar .env automáticamente usando python-dotenv si existe
load_dotenv()  # Carga variables desde .env si está presente

# Configurar CORS
front_desplegado_env = os.getenv("frontDesplegado", os.getenv("FRONT_DESPLEGADO"))
front_default = "*"
allow_origins_list = [origin for origin in [front_desplegado_env, front_default] if origin]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Leyenda CORS: Se toma la variable frontDesplegado si existe y se añade '*' para pruebas locales.

# Registrar los routers
app.include_router(citas_router)
app.include_router(paciente_router)
app.include_router(medico_router)
app.include_router(admin_router)
app.include_router(examenes_router)

# Middleware de métricas HTTP
@app.middleware("http")
async def metrics_http_middleware(request, call_next):
    start = time.perf_counter()
    response = None
    try:
        response = await call_next(request)
        return response
    finally:
        duration = time.perf_counter() - start
        # Obtener ruta normalizada (plantilla) si es posible
        route_obj = request.scope.get("route")
        route_path = getattr(route_obj, "path", None)
        method = request.method
        status_code = response.status_code if response else 500
        observe_request(method, route_path, status_code, duration)

# Endpoint /metrics
@app.get("/metrics")
async def metrics_endpoint():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

# Crear instancias
cm = CitaManager()
hc = HistorialCita()
rs = Resultados()
al = Alertas()

@app.get("/")
def read_root():
    return {"status": "active", "message": "VitalApp API is running"}

# Leyenda arquitectura:
# main.py -> registra routers (capa de entrada HTTP)
# routers -> validación ligera + dependencias de seguridad JWT
# services -> lógica de negocio (workflow, reglas)
# managers -> fachada legacy/persistencia directa JSON (en transición a repositorios)
# repositories -> abstracción de almacenamiento (JSON ahora, adaptable a SQL)

# @app.get("/diagnosticos/{paciente}/{fecha}")
# def obtener_diagnostico(paciente: str, fecha: str):
#     try:
#         diagnostico = hc.obtener_diagnostico(paciente, fecha)
#         return {"diagnostico": diagnostico}
#     except Exception as e:
#         raise HTTPException(status_code=404, detail="Diagnóstico no encontrado")
#
# @app.get("/alertas/{paciente}")
# def obtener_alertas(paciente: str):
#     try:
#         res = rs.obtener_resultados(paciente)
#         alertas = al.generar_alertas(res)
#         return {"alertas": alertas}
#     except Exception as e:
#         raise HTTPException(status_code=404, detail="No se encontraron alertas")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)