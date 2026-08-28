"""
Main FastAPI Application Server
PAIMANA & MoSPI Infrastructure Monitoring & Predictive Early Warning System
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.config import FRONTEND_DIR, DATA_DIR
from backend.routes import (
    analytics_routes,
    project_routes,
    prediction_routes,
    cuf_routes,
    ewas_routes,
    chat_routes
)
from backend.models.ml_engine import ml_engine

# Initialize FastAPI App
app = FastAPI(
    title="PAIMANA AI - Infrastructure Predictive Monitoring & Early Warning System",
    description="Ministry of Statistics and Programme Implementation (MoSPI) - IPMD Division",
    version="2.6.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(analytics_routes.router)
app.include_router(project_routes.router)
app.include_router(prediction_routes.router)
app.include_router(cuf_routes.router)
app.include_router(ewas_routes.router)
app.include_router(chat_routes.router)

# Startup event to warm up models & datasets
@app.on_event("startup")
def startup_event():
    print("[INFO] Initializing PAIMANA AI Engine...")
    csv_path = DATA_DIR / "paimana_projects_1981.csv"
    if not csv_path.exists():
        print("[INFO] Generating 1,981 PAIMANA Project Repository...")
        from backend.data_generator import save_paimana_dataset
        save_paimana_dataset()
        
    print("[INFO] Training Predictive Analytics & ML Benchmark Engines...")
    ml_engine.train_and_evaluate()
    print("[SUCCESS] PAIMANA Predictive Monitoring System Ready on http://127.0.0.1:8000")


# Mount Static Files
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/")
def serve_dashboard():
    """Serves the main single page interactive monitoring dashboard."""
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "PAIMANA AI Backend is running. Frontend index.html not found."}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "system": "PAIMANA AI Monitoring & Early Warning Platform",
        "projects_monitored": 1981,
        "ministries": 17,
        "sectors": 22
    }
