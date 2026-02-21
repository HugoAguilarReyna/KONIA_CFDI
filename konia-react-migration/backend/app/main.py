from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import auth, dashboard, kpis
from .core.database import db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    db.connect()
    yield
    # Shutdown
    db.close()

app = FastAPI(
    title="KONIA Application",
    description="Backend API for KONIA Dashboard",
    version="1.0.0",
    lifespan=lifespan
)

import os
import json

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://konia-dashboard.onrender.com",
    "https://konia-dashboard-v2.onrender.com", # Por si se renombra
]

origins_env = os.getenv("BACKEND_CORS_ORIGINS")
if origins_env:
    try:
        # Intenta parsear si viene como JSON list ["url1", "url2"]
        ext_origins = json.loads(origins_env.replace("'", '"'))
        if isinstance(ext_origins, list):
            origins.extend(ext_origins)
        else:
            origins.append(ext_origins)
    except Exception:
        # Si falla, asume que es una lista separada por comas
        ext_origins = [o.strip() for o in origins_env.split(",")]
        origins.extend(ext_origins)

# Eliminar duplicados, limpiar yasegurarse de que NO haya comodines '*'
# El navegador bloquea '*' si allow_credentials=True
origins = list(set([o.rstrip('/') for o in origins if o and o != "*"]))

if not origins:
    origins = ["https://konia-dashboard.onrender.com"]

print(f"INFO: FINAL CORS Origins configured: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(kpis.router, prefix="/api/kpis", tags=["KPIs"])

@app.get("/")
def root():
    return {"message": "KONIA API is running"}
