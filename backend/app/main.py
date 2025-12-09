# backend/app/main.py
from fastapi import FastAPI
from .routers import clientes, mascotas, citas, facturacion, auth, informes  # importa routers aquí
from .database import engine
# importa modelos para que se registren
from .models import user, client, pet, appointment, billing

app = FastAPI(title="Clínica Veterinaria - Backend")

app.include_router(clientes.router)
app.include_router(mascotas.router)
app.include_router(citas.router)
app.include_router(facturacion.router)
app.include_router(auth.router)
app.include_router(informes.router)

@app.on_event("startup")
def on_startup():
    from .database import Base
    Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "ok", "service": "clinica-veterinaria backend"}

