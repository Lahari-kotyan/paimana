"""
Early Warning Alert System (EWAS) Routes
"""

import json
from typing import Optional
from fastapi import APIRouter
from backend.config import DATA_DIR, EWAS_RULES
from backend.models.early_warning import EarlyWarningEngine

router = APIRouter(prefix="/api/ewas", tags=["Early Warning Alert System"])

def load_projects():
    json_path = DATA_DIR / "paimana_projects_1981.json"
    if not json_path.exists():
        from backend.data_generator import save_paimana_dataset
        save_paimana_dataset()
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("/alerts")
def get_portfolio_alerts(
    severity: Optional[str] = None,
    category: Optional[str] = None,
    ministry: Optional[str] = None,
    limit: int = 100
):
    """
    Scans the entire 1,981 project repository and returns triage alerts.
    """
    projects = load_projects()
    scan_res = EarlyWarningEngine.scan_portfolio_alerts(projects)
    
    alerts = scan_res["alerts"]
    if severity and severity != "ALL":
        alerts = [a for a in alerts if a["severity"].upper() == severity.upper()]
    if category and category != "ALL":
        alerts = [a for a in alerts if category.lower() in a["category"].lower()]
    if ministry and ministry != "ALL":
        alerts = [a for a in alerts if a["ministry_code"] == ministry]
        
    return {
        "total_alerts": len(alerts),
        "severity_counts": scan_res["severity_counts"],
        "category_counts": scan_res["category_counts"],
        "ministry_alert_counts": scan_res["ministry_alert_counts"],
        "alerts": alerts[:limit]
    }

@router.get("/rules")
def get_alert_rules():
    """Returns statutory EWAS trigger criteria and mitigation protocols."""
    return {"rules": EWAS_RULES}
