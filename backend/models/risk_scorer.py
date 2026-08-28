"""
Project Risk Scoring Framework (PRSF)
Computes a 5-Dimensional Composite Risk Index (0-100) for Infrastructure Projects
Calibrated for MoSPI IPMD Project Assessment
"""

from typing import Dict, Any

class ProjectRiskScorer:
    """
    Evaluates project health across 5 core risk vectors:
    1. Financial Risk (25%)
    2. Schedule & Milestone Risk (25%)
    3. Regulatory & Statutory Risk (20%)
    4. Contractor & Execution Risk (15%)
    5. Macro & Environmental Risk (15%)
    """
    
    @staticmethod
    def calculate_financial_risk(project: Dict[str, Any]) -> float:
        """Score 0-100 for financial stress, budget creep, and burn rate mismatch."""
        fin_prog = float(project.get("financial_progress_pct", 0.0))
        phys_prog = float(project.get("physical_progress_pct", 0.0))
        cost_overrun_pct = float(project.get("cost_overrun_pct", 0.0))
        
        # Mismatch penalty: money spent far exceeding physical work done
        divergence = max(0.0, fin_prog - phys_prog)
        div_score = min(100.0, divergence * 3.0)
        
        # Escalation penalty
        esc_score = min(100.0, cost_overrun_pct * 2.5)
        
        # Combined weighted financial risk
        financial_risk = (0.55 * div_score) + (0.45 * esc_score)
        return round(float(min(100.0, max(0.0, financial_risk))), 1)

    @staticmethod
    def calculate_schedule_risk(project: Dict[str, Any]) -> float:
        """Score 0-100 for milestone delays and schedule slippage."""
        delay_months = float(project.get("schedule_delay_months", 0.0))
        planned_duration = max(1.0, float(project.get("planned_duration_months", 36.0)))
        total_milestones = max(1, int(project.get("total_milestones", 10)))
        delayed_milestones = int(project.get("delayed_milestones", 0))
        critical_delay_days = float(project.get("critical_delay_days", 0.0))
        
        # Slippage ratio
        slippage_ratio = (delay_months / planned_duration) * 100.0
        slip_score = min(100.0, slippage_ratio * 1.8)
        
        # Delayed milestones ratio
        milestone_ratio = (delayed_milestones / total_milestones) * 100.0
        milestone_score = min(100.0, milestone_ratio * 1.5)
        
        # Critical days lag
        crit_score = min(100.0, (critical_delay_days / 180.0) * 100.0)
        
        schedule_risk = (0.40 * slip_score) + (0.35 * milestone_score) + (0.25 * crit_score)
        return round(float(min(100.0, max(0.0, schedule_risk))), 1)

    @staticmethod
    def calculate_regulatory_risk(project: Dict[str, Any]) -> float:
        """Score 0-100 for land acquisition bottlenecks and statutory clearances."""
        land_pct = float(project.get("land_acquired_pct", 100.0))
        forest_status = str(project.get("forest_clearance_status", "Approved"))
        elapsed_time = float(project.get("elapsed_time_pct", 0.0))
        
        # Land acquisition lag
        land_gap = max(0.0, 100.0 - land_pct)
        if elapsed_time > 40.0 and land_pct < 80.0:
            land_score = min(100.0, land_gap * 1.6)
        else:
            land_score = min(100.0, land_gap * 0.9)
            
        # Clearance penalty
        clearance_penalty_map = {
            "Stage-II Pending": 85.0,
            "Stage-I": 45.0,
            "Approved": 10.0,
            "Exempted": 0.0
        }
        forest_score = clearance_penalty_map.get(forest_status, 30.0)
        
        regulatory_risk = (0.65 * land_score) + (0.35 * forest_score)
        return round(float(min(100.0, max(0.0, regulatory_risk))), 1)

    @staticmethod
    def calculate_contractor_risk(project: Dict[str, Any]) -> float:
        """Score 0-100 for contractor quality, past disputes, and litigation load."""
        contractor_rating = float(project.get("contractor_rating", 7.0))  # 1-10
        dispute_count = int(project.get("dispute_count", 0))
        dispute_val = float(project.get("dispute_value_cr", 0.0))
        orig_cost = max(1.0, float(project.get("original_cost_cr", 500.0)))
        
        # Rating inverse score
        rating_score = max(0.0, (10.0 - contractor_rating) * 11.0)
        
        # Dispute penalty
        dispute_score = min(100.0, dispute_count * 28.0 + (dispute_val / orig_cost) * 150.0)
        
        contractor_risk = (0.50 * rating_score) + (0.50 * dispute_score)
        return round(float(min(100.0, max(0.0, contractor_risk))), 1)

    @staticmethod
    def calculate_macro_risk(project: Dict[str, Any]) -> float:
        """Score 0-100 for terrain, monsoon vulnerability, and commodity price sensitivity."""
        terrain = str(project.get("geological_terrain_risk", "Low/Plains"))
        monsoon = float(project.get("monsoon_vulnerability_index", 0.3))
        inflation_sens = float(project.get("raw_material_inflation_sensitivity", 0.4))
        
        terrain_map = {
            "High/Himalayan/Riverine": 85.0,
            "Moderate/Plateau": 45.0,
            "Low/Plains": 15.0
        }
        terrain_score = terrain_map.get(terrain, 25.0)
        monsoon_score = monsoon * 100.0
        inflation_score = inflation_sens * 100.0
        
        macro_risk = (0.40 * terrain_score) + (0.30 * monsoon_score) + (0.30 * inflation_score)
        return round(float(min(100.0, max(0.0, macro_risk))), 1)

    @classmethod
    def evaluate_project_risk(cls, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates composite project risk index (PRSF) and individual dimensional breakdowns.
        """
        fin_risk = cls.calculate_financial_risk(project)
        sched_risk = cls.calculate_schedule_risk(project)
        reg_risk = cls.calculate_regulatory_risk(project)
        cont_risk = cls.calculate_contractor_risk(project)
        macro_risk = cls.calculate_macro_risk(project)
        
        # Composite calculation with statutory IPMD weights
        composite_score = round(
            (0.25 * fin_risk) +
            (0.25 * sched_risk) +
            (0.20 * reg_risk) +
            (0.15 * cont_risk) +
            (0.15 * macro_risk),
            1
        )
        
        # Categorize
        if composite_score >= 70.0:
            category = "Critical"
            color = "#EF4444"
            badge = "CRITICAL_RISK"
        elif composite_score >= 40.0:
            category = "Moderate"
            color = "#F59E0B"
            badge = "WATCHLIST"
        else:
            category = "Low"
            color = "#10B981"
            badge = "ON_TRACK"
            
        return {
            "composite_risk_score": composite_score,
            "risk_category": category,
            "risk_color": color,
            "risk_badge": badge,
            "dimensions": {
                "financial_risk": fin_risk,
                "schedule_risk": sched_risk,
                "regulatory_risk": reg_risk,
                "contractor_risk": cont_risk,
                "macro_risk": macro_risk
            }
        }
