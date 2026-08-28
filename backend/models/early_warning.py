"""
Early Warning Alert System (EWAS) & Prescriptive Recommendation Engine
Provides automated rule and AI-triggered alerts with actionable policy & administrative interventions.
"""

from typing import List, Dict, Any
from datetime import datetime
from backend.config import EWAS_RULES

class EarlyWarningEngine:
    """
    Evaluates project data against Early Warning triggers and generates prescriptive interventions.
    """
    
    @staticmethod
    def evaluate_project_alerts(project: Dict[str, Any], predicted_overrun_pct: float = None) -> List[Dict[str, Any]]:
        """
        Evaluates a single project and returns a list of active alerts with prescriptions.
        """
        alerts = []
        
        # Extract variables
        delayed_milestones = int(project.get("delayed_milestones", 0))
        total_milestones = max(1, int(project.get("total_milestones", 10)))
        critical_delay_days = float(project.get("critical_delay_days", 0.0))
        financial_progress = float(project.get("financial_progress_pct", 0.0))
        physical_progress = float(project.get("physical_progress_pct", 0.0))
        land_acquired_pct = float(project.get("land_acquired_pct", 100.0))
        elapsed_time_pct = float(project.get("elapsed_time_pct", 0.0))
        dispute_count = int(project.get("dispute_count", 0))
        contractor_rating = float(project.get("contractor_rating", 7.0))
        forest_status = str(project.get("forest_clearance_status", "Approved"))
        cost_overrun_pct = float(project.get("cost_overrun_pct", 0.0))
        
        pred_cost_overrun = predicted_overrun_pct if predicted_overrun_pct is not None else cost_overrun_pct
        
        # 1. Critical Milestone Delay Trigger
        delayed_ratio = delayed_milestones / total_milestones
        if delayed_ratio >= 0.30 or critical_delay_days >= 60:
            alerts.append({
                "alert_id": f"EWAS-MS-{project.get('project_id', 'PRJ')}",
                "rule_id": "RULE_CRITICAL_MILESTONE",
                "severity": "CRITICAL",
                "category": "Schedule Delay",
                "title": f"Critical Milestone Delayed by {int(critical_delay_days)} Days",
                "metric_detected": f"{delayed_milestones}/{total_milestones} milestones overdue ({round(delayed_ratio*100, 1)}%)",
                "root_cause": "Key critical-path milestone bottleneck caused by equipment mobilization or contractor slowdown.",
                "prescription": "Convene Joint Review Committee with General Consultant & EPC Contractor; mandate double-shift recovery schedule.",
                "escalation_level": "Secretary / Additional Secretary (MoSPI & Line Ministry)",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            
        # 2. Burn Rate vs Physical Progress Divergence
        if (financial_progress - physical_progress >= 18.0) and (physical_progress < 60.0):
            alerts.append({
                "alert_id": f"EWAS-FIN-{project.get('project_id', 'PRJ')}",
                "rule_id": "RULE_BURN_RATE_MISMATCH",
                "severity": "CRITICAL",
                "category": "Financial Burn Rate",
                "title": "Severe Expenditure vs Physical Progress Divergence",
                "metric_detected": f"Financial Burn: {financial_progress}% vs Physical Completion: {physical_progress}% (Gap: +{round(financial_progress - physical_progress, 1)}%)",
                "root_cause": "Advance payments and material billing outpacing on-ground physical asset creation.",
                "prescription": "Depute third-party technical audit team (CAG / PMC Special Auditor) to inspect site measurement books and freeze unverified mobilization disbursements.",
                "escalation_level": "Financial Adviser / Chief Controller of Accounts",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            
        # 3. Land Acquisition Stall
        if (land_acquired_pct < 80.0) and (elapsed_time_pct >= 40.0):
            alerts.append({
                "alert_id": f"EWAS-LAND-{project.get('project_id', 'PRJ')}",
                "rule_id": "RULE_LAND_ACQUISITION_STALL",
                "severity": "HIGH",
                "category": "Right-of-Way / Land",
                "title": f"Right-of-Way Lag: Only {land_acquired_pct}% Land Handed Over",
                "metric_detected": f"Elapsed Time: {elapsed_time_pct}% vs Land Acquired: {land_acquired_pct}%",
                "root_cause": "Pending Section 19 land acquisition notifications and compensation disbursement in key revenue districts.",
                "prescription": "Escalate to Chief Secretary / State Apex RoW Taskforce; leverage PM GatiShakti NMP portal for fast-track dispute settlement.",
                "escalation_level": "State Chief Secretary & District Magistrate Taskforce",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            
        # 4. Contractor & Legal Dispute
        if dispute_count >= 2 or contractor_rating <= 4.5:
            alerts.append({
                "alert_id": f"EWAS-DISP-{project.get('project_id', 'PRJ')}",
                "rule_id": "RULE_VENDOR_DISPUTE_ESCALATION",
                "severity": "HIGH",
                "category": "Contractor & Litigation",
                "title": f"Active Contractor Disputes ({dispute_count} Claims)",
                "metric_detected": f"Disputes: {dispute_count}, Contractor Performance Rating: {contractor_rating}/10",
                "root_cause": "Sub-contractor payment frictions, change-of-scope compensation claims, or contractor capacity deficit.",
                "prescription": "Invoke Conciliation Committee under Vivad Se Vishwas II scheme to resolve claims before formal arbitration halts work.",
                "escalation_level": "Dispute Resolution Board / Ministry Legal Cell",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            
        # 5. Forest Clearance Pending
        if forest_status == "Stage-II Pending" and elapsed_time_pct >= 30.0:
            alerts.append({
                "alert_id": f"EWAS-ENV-{project.get('project_id', 'PRJ')}",
                "rule_id": "RULE_FOREST_CLEARANCE_PENDING",
                "severity": "MEDIUM",
                "category": "Statutory Clearance",
                "title": "Stage-II Forest Clearance Pending with MoEFCC",
                "metric_detected": "Forest Clearance Status: Stage-II Pending",
                "root_cause": "Compensatory afforestation land transfer pending approval by state forest department.",
                "prescription": "Fast-track joint inspection with MoEFCC Regional Empowered Committee and ensure non-forest land mutation.",
                "escalation_level": "MoEFCC Regional Office & State Principal Chief Conservator of Forests",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            
        # 6. AI Predicted Escalation
        if pred_cost_overrun >= 22.0:
            alerts.append({
                "alert_id": f"EWAS-PRED-{project.get('project_id', 'PRJ')}",
                "rule_id": "RULE_COST_OVERRUN_PREDICTED",
                "severity": "CRITICAL",
                "category": "AI Predictive Forecast",
                "title": f"AI Forecasts High Cost Escalation (+{round(pred_cost_overrun, 1)}%)",
                "metric_detected": f"Predicted Escalation: +{round(pred_cost_overrun, 1)}% above original baseline",
                "root_cause": "Compound impact of schedule delay, steel/cement inflation index, and pending statutory clearances.",
                "prescription": "Issue Early Warning Notice to IPMD Project Directorate; initiate Value Engineering review to contain scope escalation before RCE approval.",
                "escalation_level": "Cabinet Secretariat & IPMD Project Review Division",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            
        return alerts

    @classmethod
    def scan_portfolio_alerts(cls, projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Scans all 1,981 projects and aggregates portfolio-wide alert statistics.
        """
        all_alerts = []
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        category_counts = {}
        ministry_alert_counts = {}
        
        for proj in projects:
            p_alerts = cls.evaluate_project_alerts(proj)
            for a in p_alerts:
                a["project_name"] = proj.get("project_name", "")
                a["ministry_code"] = proj.get("ministry_code", "")
                a["state"] = proj.get("state", "")
                a["original_cost_cr"] = proj.get("original_cost_cr", 0.0)
                a["revised_cost_cr"] = proj.get("revised_cost_cr", 0.0)
                all_alerts.append(a)
                
                # Metrics
                sev = a["severity"]
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
                
                cat = a["category"]
                category_counts[cat] = category_counts.get(cat, 0) + 1
                
                min_code = proj.get("ministry_code", "Unknown")
                ministry_alert_counts[min_code] = ministry_alert_counts.get(min_code, 0) + 1
                
        return {
            "total_alerts": len(all_alerts),
            "severity_counts": severity_counts,
            "category_counts": category_counts,
            "ministry_alert_counts": ministry_alert_counts,
            "alerts": sorted(all_alerts, key=lambda x: 0 if x["severity"] == "CRITICAL" else (1 if x["severity"] == "HIGH" else 2))
        }
