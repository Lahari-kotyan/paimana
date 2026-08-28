"""
Analytics & Benchmarking Routes
Serves National Cockpit KPIs, Sector & Ministry Benchmarks, State Heatmaps, and Historical Trends
"""

import json
import pandas as pd
from fastapi import APIRouter
from pathlib import Path
from backend.config import DATA_DIR, STATES, MINISTRIES, SECTORS
from backend.models.risk_scorer import ProjectRiskScorer

router = APIRouter(prefix="/api/analytics", tags=["Analytics & Benchmarking"])

def get_dataframe() -> pd.DataFrame:
    csv_path = DATA_DIR / "paimana_projects_1981.csv"
    if not csv_path.exists():
        from backend.data_generator import save_paimana_dataset
        return save_paimana_dataset()
    return pd.read_csv(csv_path)

@router.get("/kpis")
def get_national_kpis():
    """Returns top-level national aggregate KPIs for Executive Cockpit."""
    df = get_dataframe()
    
    total_projects = len(df)
    total_orig_cr = float(df["original_cost_cr"].sum())
    total_rev_cr = float(df["revised_cost_cr"].sum())
    total_exp_cr = float(df["cumulative_exp_cr"].sum())
    total_overrun_cr = float(df["cost_overrun_cr"].sum())
    
    overrun_pct = round((total_overrun_cr / max(1.0, total_orig_cr)) * 100.0, 2)
    exp_pct = round((total_exp_cr / max(1.0, total_rev_cr)) * 100.0, 1)
    avg_delay = round(float(df["schedule_delay_months"].mean()), 1)
    
    delayed_projects = int((df["schedule_delay_months"] > 0).sum())
    cost_escalated_projects = int((df["cost_overrun_cr"] > 0).sum())
    critical_risk_projects = int(((df["cost_overrun_pct"] >= 20.0) | (df["schedule_delay_months"] >= 24)).sum())
    
    return {
        "total_projects": total_projects,
        "total_original_cost_lakh_cr": round(total_orig_cr / 100000.0, 2),
        "total_revised_cost_lakh_cr": round(total_rev_cr / 100000.0, 2),
        "total_cumulative_exp_lakh_cr": round(total_exp_cr / 100000.0, 2),
        "total_cost_overrun_lakh_cr": round(total_overrun_cr / 100000.0, 2),
        "total_original_cost_cr": round(total_orig_cr, 2),
        "total_revised_cost_cr": round(total_rev_cr, 2),
        "total_cumulative_exp_cr": round(total_exp_cr, 2),
        "total_cost_overrun_cr": round(total_overrun_cr, 2),
        "aggregate_overrun_pct": overrun_pct,
        "capex_disbursement_pct": exp_pct,
        "average_delay_months": avg_delay,
        "delayed_projects_count": delayed_projects,
        "delayed_projects_pct": round((delayed_projects / total_projects) * 100.0, 1),
        "cost_escalated_projects_count": cost_escalated_projects,
        "cost_escalated_projects_pct": round((cost_escalated_projects / total_projects) * 100.0, 1),
        "critical_risk_projects_count": critical_risk_projects
    }

@router.get("/sectors")
def get_sector_benchmarks():
    """Returns sector-wise capex, cost overrun, and delay metrics across 22 sectors."""
    df = get_dataframe()
    
    sector_stats = []
    grouped = df.groupby(["sector_id", "sector_name"])
    
    for (sec_id, sec_name), group in grouped:
        orig = float(group["original_cost_cr"].sum())
        rev = float(group["revised_cost_cr"].sum())
        exp = float(group["cumulative_exp_cr"].sum())
        overrun = rev - orig
        avg_delay = round(float(group["schedule_delay_months"].mean()), 1)
        overrun_pct = round((overrun / max(1.0, orig)) * 100.0, 2)
        count = len(group)
        delayed_count = int((group["schedule_delay_months"] > 0).sum())
        
        sector_stats.append({
            "sector_id": sec_id,
            "sector_name": sec_name,
            "project_count": count,
            "delayed_count": delayed_count,
            "delayed_share_pct": round((delayed_count / count) * 100.0, 1),
            "total_orig_cr": round(orig, 2),
            "total_rev_cr": round(rev, 2),
            "total_exp_cr": round(exp, 2),
            "cost_overrun_cr": round(overrun, 2),
            "cost_overrun_pct": overrun_pct,
            "avg_delay_months": avg_delay
        })
        
    sector_stats = sorted(sector_stats, key=lambda x: x["total_rev_cr"], reverse=True)
    return {"sectors": sector_stats}

@router.get("/ministries")
def get_ministry_benchmarks():
    """Returns performance across 17 Central Ministries."""
    df = get_dataframe()
    min_stats = []
    grouped = df.groupby(["ministry_code", "ministry_name"])
    
    for (m_code, m_name), group in grouped:
        orig = float(group["original_cost_cr"].sum())
        rev = float(group["revised_cost_cr"].sum())
        overrun = rev - orig
        avg_delay = round(float(group["schedule_delay_months"].mean()), 1)
        count = len(group)
        
        min_stats.append({
            "ministry_code": m_code,
            "ministry_name": m_name,
            "project_count": count,
            "total_orig_cr": round(orig, 2),
            "total_rev_cr": round(rev, 2),
            "cost_overrun_cr": round(overrun, 2),
            "cost_overrun_pct": round((overrun / max(1.0, orig)) * 100.0, 2),
            "avg_delay_months": avg_delay
        })
        
    return {"ministries": sorted(min_stats, key=lambda x: x["total_rev_cr"], reverse=True)}

@router.get("/states")
def get_state_benchmarks():
    """Returns state-wise capex and composite risk metrics for the India Geo-Spatial Map."""
    df = get_dataframe()
    state_stats = {}
    
    for state_name, s_meta in STATES.items():
        sub = df[df["state"] == state_name]
        count = len(sub)
        if count == 0:
            continue
            
        orig = float(sub["original_cost_cr"].sum())
        rev = float(sub["revised_cost_cr"].sum())
        overrun = rev - orig
        avg_delay = round(float(sub["schedule_delay_months"].mean()), 1)
        avg_cost_pct = round((overrun / max(1.0, orig)) * 100.0, 1)
        
        # Calculate average risk score
        risk_scores = [ProjectRiskScorer.evaluate_project_risk(row.to_dict())["composite_risk_score"] for _, row in sub.iterrows()]
        avg_risk = round(sum(risk_scores) / len(risk_scores), 1)
        
        state_stats[state_name] = {
            "state_name": state_name,
            "code": s_meta["code"],
            "region": s_meta["region"],
            "lat": s_meta["lat"],
            "lng": s_meta["lng"],
            "project_count": count,
            "total_orig_cr": round(orig, 2),
            "total_rev_cr": round(rev, 2),
            "cost_overrun_cr": round(overrun, 2),
            "cost_overrun_pct": avg_cost_pct,
            "avg_delay_months": avg_delay,
            "composite_risk_score": avg_risk,
            "risk_color": "#EF4444" if avg_risk >= 55 else ("#F59E0B" if avg_risk >= 40 else "#10B981")
        }
        
    return {"states": state_stats}

@router.get("/historical_trends")
def get_historical_trends():
    """Returns timeline distribution showing trends across OCMS and PAIMANA eras."""
    df = get_dataframe()
    df["start_year"] = pd.to_datetime(df["start_date"]).dt.year
    
    yearly = df.groupby("start_year").agg({
        "project_id": "count",
        "original_cost_cr": "sum",
        "revised_cost_cr": "sum",
        "cost_overrun_cr": "sum",
        "schedule_delay_months": "mean"
    }).reset_index()
    
    trends = []
    for _, row in yearly.iterrows():
        orig = float(row["original_cost_cr"])
        rev = float(row["revised_cost_cr"])
        overrun = rev - orig
        yr = int(row["start_year"])
        trends.append({
            "year": yr,
            "era": "OCMS Historical (2014-2020)" if yr <= 2020 else "PAIMANA Integrated Portal (2021-2026)",
            "project_count": int(row["project_id"]),
            "total_capex_cr": round(rev, 2),
            "cost_overrun_cr": round(overrun, 2),
            "cost_overrun_pct": round((overrun / max(1.0, orig)) * 100.0, 1),
            "avg_delay_months": round(float(row["schedule_delay_months"]), 1)
        })
        
    return {"trends": sorted(trends, key=lambda x: x["year"])}
