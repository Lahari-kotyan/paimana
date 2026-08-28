"""
LLM-Enabled Project Intelligence Assistant ("PAIMANA AI / IPMD Sahayak")
Natural Language Query Engine & MoSPI Executive Briefing Memo Generator
"""

import json
import pandas as pd
from typing import Dict, Any, List
from backend.config import DATA_DIR
from backend.models.risk_scorer import ProjectRiskScorer
from backend.models.early_warning import EarlyWarningEngine

class PAIMANAAssistant:
    """
    Intelligent Project Assistant capable of semantic querying, project triage,
    and automatic generation of MoSPI executive escalation briefs.
    """
    
    def __init__(self):
        self._load_data()
        
    def _load_data(self):
        json_path = DATA_DIR / "paimana_projects_1981.json"
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                self.projects = json.load(f)
        else:
            self.projects = []
            
    def answer_query(self, user_query: str) -> Dict[str, Any]:
        """
        Interprets natural language queries, queries the 1,981 project repository,
        and generates structured intelligence responses.
        """
        if not self.projects:
            self._load_data()
            
        q = user_query.lower()
        matched_projects = []
        
        # 1. State queries
        state_match = None
        for p in self.projects:
            if p["state"].lower() in q:
                state_match = p["state"]
                break
                
        # 2. Sector / Ministry queries
        sector_match = None
        for p in self.projects:
            if p["sector_name"].lower() in q or p["sector_id"].lower() in q or ("rail" in q and "rly" in p["sector_id"].lower()) or ("highway" in q and "hwy" in p["sector_id"].lower()) or ("solar" in q and "ren" in p["sector_id"].lower()):
                sector_match = p["sector_name"]
                break

        # Filter projects based on intent
        filtered = self.projects
        if state_match:
            filtered = [p for p in filtered if p["state"] == state_match]
        if sector_match:
            filtered = [p for p in filtered if p["sector_name"] == sector_match or ("rail" in q and "Rail" in p["sector_name"]) or ("highway" in q and "Highway" in p["sector_name"])]
            
        if "highest cost" in q or "max cost overrun" in q or "top overrun" in q:
            filtered = sorted(filtered, key=lambda x: x["cost_overrun_cr"], reverse=True)
            headline = "Top Projects Ranked by Maximum Cost Escalation (₹ Cr)"
        elif "delay" in q or "time overrun" in q or "longest delay" in q:
            filtered = sorted(filtered, key=lambda x: x["schedule_delay_months"], reverse=True)
            headline = "Projects Experiencing Longest Schedule Slippages"
        elif "critical" in q or "high risk" in q or "alert" in q:
            filtered = [p for p in filtered if p["cost_overrun_pct"] >= 20.0 or p["schedule_delay_months"] >= 24]
            headline = "Critical Infrastructure Projects on Immediate Intervention Watchlist"
        elif "dispute" in q or "contractor" in q:
            filtered = [p for p in filtered if p.get("dispute_count", 0) >= 1]
            headline = "Projects Facing Active Contractor Litigation & Claims"
        elif "land" in q:
            filtered = [p for p in filtered if p.get("land_acquired_pct", 100) < 80]
            headline = "Projects Stalled Due to Right-of-Way (RoW) / Land Acquisition Deficits"
        else:
            filtered = sorted(filtered, key=lambda x: x["original_cost_cr"], reverse=True)
            headline = "Overview of Matched Infrastructure Projects"

        top_matches = filtered[:6]
        
        # Calculate summary metrics of matched subset
        total_orig = sum(p["original_cost_cr"] for p in filtered)
        total_rev = sum(p["revised_cost_cr"] for p in filtered)
        total_overrun = total_rev - total_orig
        avg_delay = round(sum(p["schedule_delay_months"] for p in filtered) / max(1, len(filtered)), 1)
        
        # Construct dynamic response
        response_text = f"**PAIMANA Intelligence Briefing:**\n\n"
        response_text += f"Found **{len(filtered)} infrastructure projects** matching your inquiry"
        if state_match:
            response_text += f" located in **{state_match}**"
        if sector_match:
            response_text += f" under **{sector_match}**"
        response_text += f".\n\n"
        
        response_text += f"- **Aggregate Capex Monitored**: ₹{total_rev:,.2f} Cr (Original: ₹{total_orig:,.2f} Cr)\n"
        response_text += f"- **Cumulative Cost Escalation**: ₹{total_overrun:,.2f} Cr (+{round((total_overrun/max(1, total_orig))*100, 1)}%)\n"
        response_text += f"- **Average Schedule Slippage**: {avg_delay} Months\n\n"
        
        response_text += f"### {headline}:\n"
        for idx, p in enumerate(top_matches, 1):
            response_text += f"{idx}. **{p['project_name']}** (`{p['project_id']}`)\n"
            response_text += f"   - *Ministry / Sector*: {p['ministry_code']} | {p['sector_name']}\n"
            response_text += f"   - *Financials*: Orig: ₹{p['original_cost_cr']:,.1f} Cr ➔ Rev: ₹{p['revised_cost_cr']:,.1f} Cr (+₹{p['cost_overrun_cr']:,.1f} Cr, +{p['cost_overrun_pct']}%)\n"
            response_text += f"   - *Progress*: Physical: {p['physical_progress_pct']}% | Financial: {p['financial_progress_pct']}% | Delay: **{p['schedule_delay_months']} Months**\n"
            response_text += f"   - *Key Driver*: Land Acquired: {p['land_acquired_pct']}% | Disputes: {p['dispute_count']} | Forest: {p['forest_clearance_status']}\n\n"
            
        response_text += "\n> **Actionable Recommendation:** To remediate bottlenecks for these high-priority projects, consider convening an inter-ministerial coordination meeting with the respective Line Ministries and State Chief Secretaries via PM GatiShakti."

        return {
            "query": user_query,
            "response": response_text,
            "matched_count": len(filtered),
            "top_projects": top_matches
        }

    def generate_executive_brief(self, project_id: str) -> Dict[str, Any]:
        """
        Generates a formal MoSPI Executive Intervention Briefing Note for a specific project.
        """
        if not self.projects:
            self._load_data()
            
        proj = next((p for p in self.projects if p["project_id"] == project_id), None)
        if not proj:
            return {"error": f"Project ID '{project_id}' not found in PAIMANA repository."}
            
        risk = ProjectRiskScorer.evaluate_project_risk(proj)
        alerts = EarlyWarningEngine.evaluate_project_alerts(proj)
        
        memo = f"""================================================================================
CONFIDENTIAL - GOVERNMENT OF INDIA
MINISTRY OF STATISTICS AND PROGRAMME IMPLEMENTATION (MoSPI)
INFRASTRUCTURE & PROJECT MONITORING DIVISION (IPMD)
PROJECT ASSESSMENT & EARLY WARNING BRIEFING MEMORANDUM
================================================================================

1. PROJECT IDENTIFIERS & BASELINE
--------------------------------------------------------------------------------
Project Code        : {proj['project_id']}
Project Name        : {proj['project_name']}
Line Ministry       : {proj['ministry_name']} ({proj['ministry_code']})
Sector / Domain     : {proj['sector_name']}
Implementing Agency : {proj['agency_name']}
State / Region      : {proj['state']} ({proj['region']})
Current Status      : {proj['project_status']}

2. FINANCIAL & TIMELINE PERFORMANCE
--------------------------------------------------------------------------------
Original Approved Cost     : INR {proj['original_cost_cr']:,.2f} Crore
Current Revised Estimate   : INR {proj['revised_cost_cr']:,.2f} Crore
Cumulative Escalation      : INR {proj['cost_overrun_cr']:,.2f} Crore (+{proj['cost_overrun_pct']}%)
Cumulative Capex Disbursed : INR {proj['cumulative_exp_cr']:,.2f} Crore
Financial Progress Burn    : {proj['financial_progress_pct']}%
Physical Progress Verified : {proj['physical_progress_pct']}%
Original Commissioning Date: {proj['original_doc']}
Anticipated Commissioning  : {proj['anticipated_doc']}
Cumulative Schedule Delay  : {proj['schedule_delay_months']} Months ({proj['critical_delay_days']} Critical Days)

3. AI COMPOSITE RISK ASSESSMENT (PRSF SCORE: {risk['composite_risk_score']}/100 - {risk['risk_category'].upper()})
--------------------------------------------------------------------------------
- Financial Risk Vector    : {risk['dimensions']['financial_risk']}/100
- Schedule Risk Vector     : {risk['dimensions']['schedule_risk']}/100
- Regulatory Risk Vector   : {risk['dimensions']['regulatory_risk']}/100
- Contractor Risk Vector   : {risk['dimensions']['contractor_risk']}/100
- Macro & Terrain Vector   : {risk['dimensions']['macro_risk']}/100

4. CRITICAL EARLY WARNING SIGNALS & BOTTLENECK ROOT CAUSES
--------------------------------------------------------------------------------"""
        
        if alerts:
            for idx, a in enumerate(alerts, 1):
                memo += f"\n[{idx}] {a['severity']}: {a['title']}\n    • Root Cause: {a['root_cause']}\n    • Statutory Escalation: {a['escalation_level']}\n    • Recommended Action: {a['prescription']}\n"
        else:
            memo += "\nNo critical early warnings active. Project is operating within standard variance tolerances.\n"
            
        memo += f"""
5. PRESCRIPTIVE POLICY & ADMINISTRATIVE INTERVENTION DIRECTIVE
--------------------------------------------------------------------------------
1. Institutional Escalation: Line Ministry Secretary to convene joint task force with {proj['agency_name']}.
2. RoW & Land Resolution: Expedite remaining {round(100.0 - proj['land_acquired_pct'], 1)}% land acquisition via PM GatiShakti National Master Plan.
3. Contractual Settlement: Initiate dispute conciliation under Vivad Se Vishwas II to avoid arbitration delays.
4. Monitoring Cadence: Place on Fortnightly High-Level IPMD Monitoring Dashboard.

================================================================================
Generated via PAIMANA AI Early Warning Engine | MoSPI New Delhi
================================================================================"""

        return {
            "project_id": project_id,
            "project_name": proj["project_name"],
            "brief_text": memo,
            "risk_evaluation": risk,
            "alerts": alerts
        }

# Global singleton
paimana_assistant = PAIMANAAssistant()
