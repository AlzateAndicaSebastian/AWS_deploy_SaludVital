from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from app.managers.cita_manager import CitaManager
from app.managers.historial_cita import HistorialCita
from app.managers.resultados import Resultados
from app.managers.alertas import Alertas
from app.routers.citas_router import router as citas_router

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

# Crear instancias
cm = CitaManager()
hc = HistorialCita()
rs = Resultados()
al = Alertas()

@app.get("/")
def read_root():
    return {"status": "active", "message": "VitalApp API is running"}

@app.post("/citas")
def crear_cita(paciente: str, medico: str, fecha: str):
    try:
        cm.agendar_cita(paciente, medico, fecha)
        return {"message": "Cita creada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/diagnosticos/{paciente}/{fecha}")
def obtener_diagnostico(paciente: str, fecha: str):
    try:
        diagnostico = hc.obtener_diagnostico(paciente, fecha)
        return {"diagnostico": diagnostico}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Diagnóstico no encontrado")

@app.get("/alertas/{paciente}")
def obtener_alertas(paciente: str):
    try:
        res = rs.obtener_resultados(paciente)
        alertas = al.generar_alertas(res)
        return {"alertas": alertas}
    except Exception as e:
        raise HTTPException(status_code=404, detail="No se encontraron alertas")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)