"""
Common Upload Form (CUF) Ingestion, Validation & Audit Routes
"""

import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from backend.config import MINISTRIES, SECTORS, STATES, DATA_DIR
from backend.models.risk_scorer import ProjectRiskScorer
from backend.models.ml_engine import ml_engine

router = APIRouter(prefix="/api/cuf", tags=["Common Upload Form (CUF) Pipeline"])

class CUFRecord(BaseModel):
    project_id: str
    project_name: str
    ministry_code: str
    sector_id: str
    state: str
    agency_name: str
    original_cost_cr: float
    revised_cost_cr: float
    cumulative_exp_cr: float
    physical_progress_pct: float
    original_doc: str
    anticipated_doc: str
    total_milestones: int
    delayed_milestones: int
    land_acquired_pct: Optional[float] = 100.0
    contractor_rating: Optional[float] = 7.0
    dispute_count: Optional[int] = 0

class CUFBatchValidateRequest(BaseModel):
    records: List[Dict[str, Any]]

@router.get("/schema")
def get_cuf_schema():
    """Returns official PAIMANA Common Upload Form field specifications."""
    return {
        "cuf_version": "PAIMANA-CUF-v2.6",
        "description": "Standardized Monthly Project Progress Common Upload Form for MoSPI IPMD Monitoring",
        "required_fields": [
            {"name": "project_id", "type": "string", "example": "PAIMANA-HWY-2023-1042", "description": "Unique National Project Identifier"},
            {"name": "project_name", "type": "string", "example": "Delhi-Meerut Expressway Package 3", "description": "Official Approved Project Name"},
            {"name": "ministry_code", "type": "string", "example": "MoRTH", "description": "Nodal Central Ministry Code"},
            {"name": "sector_id", "type": "string", "example": "SEC_HWY", "description": "22 Monitored Infrastructure Sector Codes"},
            {"name": "state", "type": "string", "example": "Uttar Pradesh", "description": "Primary State / UT of Project Site"},
            {"name": "agency_name", "type": "string", "example": "NHAI", "description": "Executing Agency / PSU Name"},
            {"name": "original_cost_cr", "type": "float", "example": 1450.0, "description": "Original Approved Cost (>= ₹150 Cr)"},
            {"name": "revised_cost_cr", "type": "float", "example": 1620.0, "description": "Current Revised Cost Estimate (₹ Cr)"},
            {"name": "cumulative_exp_cr", "type": "float", "example": 780.0, "description": "Cumulative Expenditure Incurred (₹ Cr)"},
            {"name": "physical_progress_pct", "type": "float", "example": 54.2, "description": "Physical Progress Completed (%)"},
            {"name": "original_doc", "type": "string", "example": "2025-12-31", "description": "Original Date of Commissioning (YYYY-MM-DD)"},
            {"name": "anticipated_doc", "type": "string", "example": "2026-06-30", "description": "Anticipated Date of Commissioning (YYYY-MM-DD)"},
            {"name": "total_milestones", "type": "int", "example": 24, "description": "Total Stage-Gate Milestones Scheduled"},
            {"name": "delayed_milestones", "type": "int", "example": 4, "description": "Count of Overdue / Delayed Milestones"}
        ],
        "augmented_optional_fields": [
            {"name": "land_acquired_pct", "type": "float", "example": 88.5, "description": "Right-of-Way Land Handover Progress (%)"},
            {"name": "contractor_rating", "type": "float", "example": 7.5, "description": "Contractor Track Record Rating (1-10)"},
            {"name": "dispute_count", "type": "int", "example": 1, "description": "Active Contractor Claims / Arbitrations Count"}
        ]
    }

@router.post("/validate")
def validate_cuf_records(req: CUFBatchValidateRequest):
    """
    Validates batch CUF records against schema rules, detects data anomalies,
    and performs instant AI Risk Audits on validated projects.
    """
    results = []
    valid_count = 0
    invalid_count = 0
    
    valid_ministry_codes = {m["code"] for m in MINISTRIES}
    valid_sector_ids = {s["id"] for s in SECTORS}
    valid_states = set(STATES.keys())
    
    for idx, rec in enumerate(req.records, 1):
        errors = []
        warnings = []
        
        # Validation checks
        if not rec.get("project_id"):
            errors.append("Missing 'project_id'.")
        if not rec.get("project_name"):
            errors.append("Missing 'project_name'.")
            
        m_code = rec.get("ministry_code")
        if not m_code or m_code not in valid_ministry_codes:
            errors.append(f"Invalid ministry_code '{m_code}'. Must be one of 17 Central Ministries.")
            
        s_id = rec.get("sector_id")
        if not s_id or s_id not in valid_sector_ids:
            errors.append(f"Invalid sector_id '{s_id}'. Must be one of 22 Monitored Sectors.")
            
        st = rec.get("state")
        if not st or st not in valid_states:
            warnings.append(f"State '{st}' not matched in standard registry.")
            
        orig_cost = float(rec.get("original_cost_cr", 0.0))
        if orig_cost < 150.0:
            warnings.append(f"Original Cost ₹{orig_cost} Cr is below MoSPI ₹150 Cr threshold.")
            
        rev_cost = float(rec.get("revised_cost_cr", orig_cost))
        exp = float(rec.get("cumulative_exp_cr", 0.0))
        
        if exp > rev_cost:
            errors.append(f"Cumulative expenditure (₹{exp} Cr) exceeds revised cost (₹{rev_cost} Cr).")
            
        phys_prog = float(rec.get("physical_progress_pct", 0.0))
        if phys_prog < 0.0 or phys_prog > 100.0:
            errors.append(f"Physical progress {phys_prog}% out of 0-100 range.")
            
        # Financial Progress Burn vs Physical divergence
        fin_prog = round((exp / max(1.0, rev_cost)) * 100.0, 1)
        if (fin_prog - phys_prog >= 20.0) and (phys_prog < 50.0):
            warnings.append(f"Anomaly: Financial burn ({fin_prog}%) significantly outpaces physical progress ({phys_prog}%).")
            
        # Audit status
        is_valid = len(errors) == 0
        if is_valid:
            valid_count += 1
            # Run instant risk and ML evaluation
            rec_enriched = dict(rec)
            rec_enriched["cost_overrun_cr"] = round(max(0.0, rev_cost - orig_cost), 2)
            rec_enriched["cost_overrun_pct"] = round(((rev_cost - orig_cost) / max(1.0, orig_cost)) * 100.0, 2)
            rec_enriched["financial_progress_pct"] = fin_prog
            rec_enriched["planned_duration_months"] = 36
            rec_enriched["schedule_delay_months"] = 6
            rec_enriched["elapsed_time_pct"] = 50.0
            rec_enriched["critical_delay_days"] = 90
            
            risk_audit = ProjectRiskScorer.evaluate_project_risk(rec_enriched)
            pred = ml_engine.predict_project(rec_enriched)
        else:
            invalid_count += 1
            risk_audit = None
            pred = None
            
        results.append({
            "record_index": idx,
            "project_id": rec.get("project_id", f"REC_{idx}"),
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "risk_audit": risk_audit,
            "ml_prediction": pred
        })
        
    return {
        "total_submitted": len(req.records),
        "valid_count": valid_count,
        "invalid_count": invalid_count,
        "results": results
    }

@router.get("/sample_template")
def get_sample_cuf_template():
    """Returns sample records for CUF template demonstration."""
    return [
        {
            "project_id": "PAIMANA-HWY-2024-9001",
            "project_name": "Bengaluru-Chennai Expressway Section 4",
            "ministry_code": "MoRTH",
            "sector_id": "SEC_HWY",
            "state": "Karnataka",
            "agency_name": "NHAI",
            "original_cost_cr": 2400.0,
            "revised_cost_cr": 2680.0,
            "cumulative_exp_cr": 1340.0,
            "physical_progress_pct": 52.5,
            "original_doc": "2026-03-31",
            "anticipated_doc": "2026-09-30",
            "total_milestones": 24,
            "delayed_milestones": 3,
            "land_acquired_pct": 92.0,
            "contractor_rating": 8.0,
            "dispute_count": 0
        },
        {
            "project_id": "PAIMANA-RLY-2023-9002",
            "project_name": "Son Nagar to Dankuni Dedicated Freight Corridor Link",
            "ministry_code": "MoR",
            "sector_id": "SEC_RLY",
            "state": "West Bengal",
            "agency_name": "DFCCIL",
            "original_cost_cr": 4500.0,
            "revised_cost_cr": 5350.0,
            "cumulative_exp_cr": 2100.0,
            "physical_progress_pct": 38.0,
            "original_doc": "2025-10-31",
            "anticipated_doc": "2027-04-30",
            "total_milestones": 32,
            "delayed_milestones": 8,
            "land_acquired_pct": 74.5,
            "contractor_rating": 5.5,
            "dispute_count": 2
        }
    ]
