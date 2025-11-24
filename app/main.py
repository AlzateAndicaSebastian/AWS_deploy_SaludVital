from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from app.managers.cita_manager import CitaManager
from app.managers.historial_cita import HistorialCita
from app.managers.resultados import Resultados
from app.managers.alertas import Alertas
from app.routers.citas_router import router as citas_router
from app.routers.paciente_router import router as paciente_router
from app.routers.medico_router import router as medico_router
from app.routers.admin_router import router as admin_router
from app.routers.examenes_router import router as examenes_router

app = FastAPI(title="VitalApp API")

# Configurar CORS
front_desplegado = os.getenv("frontDesplegado", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[front_desplegado],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar los routers
app.include_router(citas_router)
app.include_router(paciente_router)
app.include_router(medico_router)
app.include_router(admin_router)
app.include_router(examenes_router)

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