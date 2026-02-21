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
origins_env = os.getenv("BACKEND_CORS_ORIGINS")
if origins_env:
    try:
        # Intenta parsear si viene como JSON list ["url1", "url2"]
        origins = json.loads(origins_env.replace("'", '"'))
    except Exception:
        # Si falla, asume que es una sola URL o lista separada por comas
        origins = [o.strip() for o in origins_env.split(",")]
else:
    origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

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
