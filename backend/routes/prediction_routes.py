"""
Predictive Analytics, Benchmarks, What-If Simulation & CUF Attribution Routes
"""

from typing import Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from backend.models.ml_engine import ml_engine
from backend.models.cuf_attribution import CUFAttributionEngine

router = APIRouter(prefix="/api/predict", tags=["Predictive Analytics & Simulation"])

class PredictRequest(BaseModel):
    project_data: Dict[str, Any]

class SimulateRequest(BaseModel):
    base_project: Dict[str, Any]
    adjustments: Dict[str, Any]

@router.get("/benchmarks")
def get_model_benchmarks():
    """
    Returns empirical evaluation comparing Statistical Baselines vs AI/ML Models.
    """
    if not ml_engine.is_trained:
        ml_engine.train_and_evaluate()
    return ml_engine.benchmarks

@router.post("/project")
def predict_project(req: PredictRequest):
    """
    Predicts Cost & Schedule Overruns for an infrastructure project.
    """
    try:
        res = ml_engine.predict_project(req.project_data)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulate")
def simulate_scenario(req: SimulateRequest):
    """
    What-If Sandbox: Simulates adjustments in project variables and returns delta impact.
    """
    try:
        res = ml_engine.simulate_what_if(req.base_project, req.adjustments)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cuf_attribution")
def get_cuf_attribution():
    """
    Returns empirical feature attribution analysis comparing native CUF vs augmented indicators.
    """
    return CUFAttributionEngine.run_attribution_study()
