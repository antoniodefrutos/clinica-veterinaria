from fastapi import FastAPI

app = FastAPI(
    title="API Clínica Veterinaria",
    version="0.1.0",
    description="API para gestionar pacientes, citas y facturación de la clínica veterinaria.",
)


@app.get("/health")
def health_check():
    """
    Endpoint sencillo para comprobar que la API está funcionando.
    """
    return {"status": "ok"}
