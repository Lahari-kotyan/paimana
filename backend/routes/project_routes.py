"""
Project Management & 360° Explorer Routes
Provides search, multi-faceted filtering, project dossier, and S-Curve trajectory graphs
"""

import json
import pandas as pd
import numpy as np
from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from backend.config import DATA_DIR
from backend.models.risk_scorer import ProjectRiskScorer
from backend.models.early_warning import EarlyWarningEngine
from backend.models.ml_engine import ml_engine

router = APIRouter(prefix="/api/projects", tags=["Project Explorer"])

def load_projects_json():
    json_path = DATA_DIR / "paimana_projects_1981.json"
    if not json_path.exists():
        from backend.data_generator import save_paimana_dataset
        save_paimana_dataset()
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("")
def list_projects(
    search: Optional[str] = None,
    ministry: Optional[str] = None,
    sector: Optional[str] = None,
    state: Optional[str] = None,
    risk_level: Optional[str] = None,
    status: Optional[str] = None,
    min_cost: Optional[float] = None,
    max_cost: Optional[float] = None,
    min_delay: Optional[int] = None,
    sort_by: str = "revised_cost_cr",
    sort_order: str = "desc",
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=200)
):
    """
    Search and filter through the 1,981 PAIMANA infrastructure projects.
    """
    projects = load_projects_json()
    
    # Filter
    filtered = projects
    
    if search:
        s_lower = search.lower().strip()
        filtered = [
            p for p in filtered
            if s_lower in p["project_name"].lower()
            or s_lower in p["project_id"].lower()
            or s_lower in p["agency_name"].lower()
            or s_lower in p["state"].lower()
        ]
        
    if ministry and ministry != "ALL":
        filtered = [p for p in filtered if p["ministry_code"] == ministry]
        
    if sector and sector != "ALL":
        filtered = [p for p in filtered if p["sector_id"] == sector]
        
    if state and state != "ALL":
        filtered = [p for p in filtered if p["state"] == state]
        
    if status and status != "ALL":
        filtered = [p for p in filtered if p["project_status"] == status]
        
    if min_cost is not None:
        filtered = [p for p in filtered if p["revised_cost_cr"] >= min_cost]
        
    if max_cost is not None:
        filtered = [p for p in filtered if p["revised_cost_cr"] <= max_cost]
        
    if min_delay is not None:
        filtered = [p for p in filtered if p["schedule_delay_months"] >= min_delay]
        
    # Evaluate risk for each project (and filter if specified)
    enriched = []
    for p in filtered:
        risk_res = ProjectRiskScorer.evaluate_project_risk(p)
        p_copy = dict(p)
        p_copy["composite_risk_score"] = risk_res["composite_risk_score"]
        p_copy["risk_category"] = risk_res["risk_category"]
        p_copy["risk_color"] = risk_res["risk_color"]
        
        if risk_level and risk_level != "ALL":
            if risk_res["risk_category"].upper() != risk_level.upper():
                continue
                
        enriched.append(p_copy)
        
    # Sort
    reverse = (sort_order.lower() == "desc")
    if sort_by in ["revised_cost_cr", "original_cost_cr", "cost_overrun_cr", "cost_overrun_pct", "schedule_delay_months", "physical_progress_pct", "financial_progress_pct", "composite_risk_score"]:
        enriched = sorted(enriched, key=lambda x: x.get(sort_by, 0), reverse=reverse)
    else:
        enriched = sorted(enriched, key=lambda x: str(x.get(sort_by, "")), reverse=reverse)
        
    total_count = len(enriched)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    page_items = enriched[start_idx:end_idx]
    
    return {
        "total": total_count,
        "page": page,
        "limit": limit,
        "total_pages": (total_count + limit - 1) // limit,
        "projects": page_items
    }

@router.get("/dropdown/list")
def get_dropdown_projects():
    """
    Returns lightweight identifier and summary records for all 1,981 projects.
    """
    projects = load_projects_json()
    return [
        {
            "project_id": p["project_id"],
            "project_name": p["project_name"],
            "ministry_code": p["ministry_code"],
            "sector_name": p["sector_name"],
            "state": p["state"],
            "agency_name": p.get("agency_name", ""),
            "revised_cost_cr": p.get("revised_cost_cr", 0.0),
            "original_cost_cr": p.get("original_cost_cr", 0.0),
            "cost_overrun_cr": p.get("cost_overrun_cr", 0.0),
            "cost_overrun_pct": p.get("cost_overrun_pct", 0.0),
            "physical_progress_pct": p.get("physical_progress_pct", 0.0),
            "financial_progress_pct": p.get("financial_progress_pct", 0.0),
            "schedule_delay_months": p.get("schedule_delay_months", 0),
            "anticipated_doc": p.get("anticipated_doc", p.get("original_doc", "")),
            "original_doc": p.get("original_doc", ""),
            "location_lat": p.get("location_lat", 0.0),
            "location_lng": p.get("location_lng", 0.0)
        }
        for p in projects
    ]

@router.get("/{project_id}")
def get_project_detail(project_id: str):
    """
    Returns full 360° Project Dossier including Risk vectors, EWAS alerts, and AI predictions.
    """
    projects = load_projects_json()
    proj = next((p for p in projects if p["project_id"] == project_id), None)
    if not proj:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")
        
    # Risk Scoring
    risk_evaluation = ProjectRiskScorer.evaluate_project_risk(proj)
    
    # ML Prediction
    ml_prediction = ml_engine.predict_project(proj)
    
    # Alerts
    alerts = EarlyWarningEngine.evaluate_project_alerts(proj, predicted_overrun_pct=ml_prediction["predicted_cost_overrun_pct"])
    
    return {
        "project": proj,
        "risk_evaluation": risk_evaluation,
        "ml_prediction": ml_prediction,
        "active_alerts": alerts
    }

@router.get("/{project_id}/s_curve")
def get_project_s_curve(project_id: str):
    """
    Generates time-series S-Curve for Planned vs Actual vs AI-Predicted trajectory.
    """
    projects = load_projects_json()
    proj = next((p for p in projects if p["project_id"] == project_id), None)
    if not proj:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")
        
    planned_mo = max(12, int(proj.get("planned_duration_months", 36)))
    delay_mo = int(proj.get("schedule_delay_months", 0))
    total_mo = planned_mo + delay_mo
    
    orig_cost = float(proj.get("original_cost_cr", 1000.0))
    rev_cost = float(proj.get("revised_cost_cr", orig_cost))
    current_exp = float(proj.get("cumulative_exp_cr", orig_cost * 0.4))
    
    # Compute elapsed months based on elapsed_time_pct
    elapsed_pct = float(proj.get("elapsed_time_pct", 50.0))
    elapsed_mo = int(min(total_mo, (elapsed_pct / 100.0) * planned_mo))
    
    labels = []
    planned_curve = []
    actual_curve = []
    predicted_curve = []
    
    # Logistic S-curve mathematical formula
    for m in range(0, total_mo + 1, max(1, total_mo // 15)):
        labels.append(f"M{m}")
        
        # Planned S-Curve (ends at planned_mo with orig_cost)
        if m <= planned_mo:
            t = (m / planned_mo) * 6 - 3
            p_val = round(orig_cost / (1 + np.exp(-t)), 1)
        else:
            p_val = orig_cost
        planned_curve.append(p_val)
        
        # Actual S-Curve (only up to elapsed_mo)
        if m <= elapsed_mo:
            if elapsed_mo > 0:
                t_act = (m / elapsed_mo) * 6 - 3
                act_val = round(current_exp / (1 + np.exp(-t_act)), 1)
            else:
                act_val = 0
            actual_curve.append(act_val)
            predicted_curve.append(act_val)
        else:
            actual_curve.append(None)
            # Predicted future curve (approaching rev_cost by total_mo)
            rem_mo = max(1, total_mo - elapsed_mo)
            curr_step = m - elapsed_mo
            pred_progress = (curr_step / rem_mo) ** 1.3
            pred_val = round(current_exp + (rev_cost - current_exp) * pred_progress, 1)
            predicted_curve.append(pred_val)
            
    return {
        "project_id": project_id,
        "project_name": proj["project_name"],
        "labels": labels,
        "planned_capex_cr": planned_curve,
        "actual_capex_cr": actual_curve,
        "predicted_capex_cr": predicted_curve,
        "original_cost_cr": orig_cost,
        "revised_cost_cr": rev_cost,
        "cumulative_exp_cr": current_exp
    }
