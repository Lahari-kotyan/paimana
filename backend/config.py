"""
PAIMANA & OCMS Infrastructure Monitoring System Configuration
Ministry of Statistics and Programme Implementation (MoSPI) - IPMD Division
"""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
DATA_DIR = BACKEND_DIR / "data"
FRONTEND_DIR = BASE_DIR / "frontend"
MODELS_DIR = BACKEND_DIR / "models"
DOCS_DIR = BASE_DIR / "docs"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)

# MoSPI / PAIMANA Benchmark Figures (April 2026 Target Portfolio)
TOTAL_PROJECTS = 1981
TARGET_ORIGINAL_COST_LAKH_CR = 37.13
TARGET_REVISED_COST_LAKH_CR = 42.78
TARGET_CUMULATIVE_EXP_LAKH_CR = 20.36
MIN_PROJECT_COST_CR = 150.0  # ₹150 Cr threshold for MoSPI IPMD monitoring

# 17 Central Ministries
MINISTRIES = [
    {"code": "MoRTH", "name": "Ministry of Road Transport and Highways", "weight": 0.38},
    {"code": "MoR", "name": "Ministry of Railways", "weight": 0.24},
    {"code": "MoPNG", "name": "Ministry of Petroleum and Natural Gas", "weight": 0.12},
    {"code": "MoP", "name": "Ministry of Power", "weight": 0.08},
    {"code": "MoCoal", "name": "Ministry of Coal", "weight": 0.04},
    {"code": "MoHUA", "name": "Ministry of Housing and Urban Affairs", "weight": 0.04},
    {"code": "MoPSW", "name": "Ministry of Ports, Shipping and Waterways", "weight": 0.02},
    {"code": "MoCA", "name": "Ministry of Civil Aviation", "weight": 0.02},
    {"code": "MoSteel", "name": "Ministry of Steel", "weight": 0.015},
    {"code": "MNRE", "name": "Ministry of New and Renewable Energy", "weight": 0.015},
    {"code": "DoT", "name": "Department of Telecommunications", "weight": 0.01},
    {"code": "DAE", "name": "Department of Atomic Energy", "weight": 0.01},
    {"code": "DoWR", "name": "Department of Water Resources, RD & GR", "weight": 0.01},
    {"code": "MoCF", "name": "Ministry of Chemicals and Fertilizers", "weight": 0.01},
    {"code": "MoMines", "name": "Ministry of Mines", "weight": 0.008},
    {"code": "MoHFW", "name": "Ministry of Health and Family Welfare", "weight": 0.007},
    {"code": "MHI", "name": "Ministry of Heavy Industries", "weight": 0.005},
]

# 22 Infrastructure Sectors
SECTORS = [
    {"id": "SEC_HWY", "name": "Highways & Expressways", "ministry": "MoRTH", "avg_cost": 2100, "delay_risk": 0.65},
    {"id": "SEC_RLY", "name": "Railways & High-Speed Rail", "ministry": "MoR", "avg_cost": 3400, "delay_risk": 0.72},
    {"id": "SEC_PET", "name": "Petroleum Pipelines & Refineries", "ministry": "MoPNG", "avg_cost": 4800, "delay_risk": 0.42},
    {"id": "SEC_PWR_TR", "name": "Power Transmission & Grid", "ministry": "MoP", "avg_cost": 1250, "delay_risk": 0.35},
    {"id": "SEC_PWR_GEN", "name": "Thermal & Hydro Power Generation", "ministry": "MoP", "avg_cost": 5600, "delay_risk": 0.68},
    {"id": "SEC_REN", "name": "Solar & Renewable Green Energy", "ministry": "MNRE", "avg_cost": 950, "delay_risk": 0.28},
    {"id": "SEC_COAL", "name": "Coal Mining & Washeries", "ministry": "MoCoal", "avg_cost": 1800, "delay_risk": 0.55},
    {"id": "SEC_METRO", "name": "Metro Rail & Urban Transit", "ministry": "MoHUA", "avg_cost": 6200, "delay_risk": 0.60},
    {"id": "SEC_PORT", "name": "Major Ports & Maritime Channels", "ministry": "MoPSW", "avg_cost": 1650, "delay_risk": 0.48},
    {"id": "SEC_AIR", "name": "Regional & Greenfield Airports", "ministry": "MoCA", "avg_cost": 2400, "delay_risk": 0.40},
    {"id": "SEC_STEEL", "name": "Steel Plants & Metallurgy Units", "ministry": "MoSteel", "avg_cost": 4100, "delay_risk": 0.50},
    {"id": "SEC_TEL", "name": "Telecommunication & BharatNet Fiber", "ministry": "DoT", "avg_cost": 1100, "delay_risk": 0.58},
    {"id": "SEC_ATOM", "name": "Atomic Energy & Nuclear Power", "ministry": "DAE", "avg_cost": 12500, "delay_risk": 0.78},
    {"id": "SEC_WATER", "name": "Water Supply & Urban Sanitation", "ministry": "MoHUA", "avg_cost": 650, "delay_risk": 0.45},
    {"id": "SEC_IRR", "name": "National River Link & Irrigation", "ministry": "DoWR", "avg_cost": 3200, "delay_risk": 0.82},
    {"id": "SEC_CHEM", "name": "Fertilizer Plants & Petrochemicals", "ministry": "MoCF", "avg_cost": 3100, "delay_risk": 0.44},
    {"id": "SEC_MINE", "name": "Strategic Mineral Extraction", "ministry": "MoMines", "avg_cost": 1400, "delay_risk": 0.52},
    {"id": "SEC_HEALTH", "name": "AIIMS & Super-Specialty Medical Infra", "ministry": "MoHFW", "avg_cost": 1350, "delay_risk": 0.49},
    {"id": "SEC_LOG", "name": "Multimodal Logistics Parks (MMLP)", "ministry": "MoRTH", "avg_cost": 1850, "delay_risk": 0.38},
    {"id": "SEC_HEAVY", "name": "Heavy Engineering & Capital Goods", "ministry": "MHI", "avg_cost": 850, "delay_risk": 0.36},
    {"id": "SEC_INLAND", "name": "National Waterways & River Ports", "ministry": "MoPSW", "avg_cost": 920, "delay_risk": 0.51},
    {"id": "SEC_SMART", "name": "Smart Cities & Industrial Corridors", "ministry": "MoHUA", "avg_cost": 2900, "delay_risk": 0.53},
]

# States & Union Territories with Geographic Lat/Long Coordinates and Region
STATES = {
    "Maharashtra": {"lat": 19.7515, "lng": 75.7139, "region": "West", "code": "MH", "projects_wt": 0.11},
    "Uttar Pradesh": {"lat": 26.8467, "lng": 80.9462, "region": "North", "code": "UP", "projects_wt": 0.10},
    "Tamil Nadu": {"lat": 11.1271, "lng": 78.6569, "region": "South", "code": "TN", "projects_wt": 0.08},
    "Gujarat": {"lat": 22.2587, "lng": 71.1924, "region": "West", "code": "GJ", "projects_wt": 0.08},
    "Karnataka": {"lat": 15.3173, "lng": 75.7139, "region": "South", "code": "KA", "projects_wt": 0.07},
    "Madhya Pradesh": {"lat": 22.9734, "lng": 78.6569, "region": "Central", "code": "MP", "projects_wt": 0.06},
    "Andhra Pradesh": {"lat": 15.9129, "lng": 79.7400, "region": "South", "code": "AP", "projects_wt": 0.06},
    "Rajasthan": {"lat": 27.0238, "lng": 74.2179, "region": "North", "code": "RJ", "projects_wt": 0.05},
    "West Bengal": {"lat": 22.9868, "lng": 87.8550, "region": "East", "code": "WB", "projects_wt": 0.05},
    "Odisha": {"lat": 20.9517, "lng": 85.0985, "region": "East", "code": "OD", "projects_wt": 0.05},
    "Bihar": {"lat": 25.0961, "lng": 85.3131, "region": "East", "code": "BR", "projects_wt": 0.04},
    "Telangana": {"lat": 18.1124, "lng": 79.0193, "region": "South", "code": "TS", "projects_wt": 0.04},
    "Kerala": {"lat": 10.8505, "lng": 76.2711, "region": "South", "code": "KL", "projects_wt": 0.03},
    "Jharkhand": {"lat": 23.6102, "lng": 85.2799, "region": "East", "code": "JH", "projects_wt": 0.03},
    "Assam": {"lat": 26.2006, "lng": 92.9376, "region": "North-East", "code": "AS", "projects_wt": 0.03},
    "Haryana": {"lat": 29.0588, "lng": 76.0856, "region": "North", "code": "HR", "projects_wt": 0.03},
    "Punjab": {"lat": 31.1471, "lng": 75.3412, "region": "North", "code": "PB", "projects_wt": 0.025},
    "Chhattisgarh": {"lat": 21.2787, "lng": 81.8661, "region": "Central", "code": "CG", "projects_wt": 0.025},
    "Jammu & Kashmir": {"lat": 33.7782, "lng": 76.5762, "region": "North", "code": "JK", "projects_wt": 0.02},
    "Uttarakhand": {"lat": 30.0668, "lng": 79.0193, "region": "North", "code": "UK", "projects_wt": 0.015},
    "Himachal Pradesh": {"lat": 31.1048, "lng": 77.1734, "region": "North", "code": "HP", "projects_wt": 0.01},
    "Delhi NCR": {"lat": 28.7041, "lng": 77.1025, "region": "North", "code": "DL", "projects_wt": 0.015},
    "Goa": {"lat": 15.2993, "lng": 74.1240, "region": "West", "code": "GA", "projects_wt": 0.005},
    "Arunachal Pradesh": {"lat": 28.2180, "lng": 94.7278, "region": "North-East", "code": "AR", "projects_wt": 0.005},
    "Meghalaya": {"lat": 25.4670, "lng": 91.3662, "region": "North-East", "code": "ML", "projects_wt": 0.005},
    "Manipur": {"lat": 24.6637, "lng": 93.9063, "region": "North-East", "code": "MN", "projects_wt": 0.004},
    "Tripura": {"lat": 23.9408, "lng": 91.9882, "region": "North-East", "code": "TR", "projects_wt": 0.003},
    "Nagaland": {"lat": 26.1584, "lng": 94.5624, "region": "North-East", "code": "NL", "projects_wt": 0.003},
    "Mizoram": {"lat": 23.1645, "lng": 92.9376, "region": "North-East", "code": "MZ", "projects_wt": 0.002},
    "Sikkim": {"lat": 27.5330, "lng": 88.5122, "region": "North-East", "code": "SK", "projects_wt": 0.002},
    "Multi-State / National": {"lat": 22.0000, "lng": 79.0000, "region": "National", "code": "NAT", "projects_wt": 0.031}
}

# Project Status
PROJECT_STATUSES = ["Ongoing", "Under Implementation", "Nearing Completion", "Stalled/Delayed", "Commissioned"]

# Risk Thresholds
RISK_LEVELS = {
    "LOW": {"min": 0, "max": 39.9, "label": "On-Track / Low Risk", "color": "#10B981"},
    "MEDIUM": {"min": 40.0, "max": 69.9, "label": "Moderate / Watchlist", "color": "#F59E0B"},
    "HIGH": {"min": 70.0, "max": 100.0, "label": "Critical / High Overrun Risk", "color": "#EF4444"}
}

# Early Warning Trigger Rules
EWAS_RULES = [
    {
        "id": "RULE_CRITICAL_MILESTONE",
        "name": "Critical Stage-Gate Delay",
        "condition": "delayed_milestones_ratio >= 0.33 or critical_delay_days >= 60",
        "severity": "CRITICAL",
        "category": "Schedule",
        "prescription": "Convene Joint Review Committee with General Consultant & EPC Contractor; initiate 24/7 double-shift recovery schedule."
    },
    {
        "id": "RULE_BURN_RATE_MISMATCH",
        "name": "Expenditure vs Physical Progress Divergence",
        "condition": "financial_progress - physical_progress >= 20.0 and physical_progress < 50.0",
        "severity": "CRITICAL",
        "category": "Financial",
        "prescription": "Deploy third-party technical & financial auditor (CAG/PMC) to verify measurement books and curb unchecked bill clearing."
    },
    {
        "id": "RULE_LAND_ACQUISITION_STALL",
        "name": "Land Acquisition Bottleneck",
        "condition": "land_acquired_pct < 80.0 and elapsed_time_pct >= 40.0",
        "severity": "HIGH",
        "category": "Regulatory",
        "prescription": "Escalate to Chief Secretary / State Apex RoW Taskforce; expedite Section 19 land award disbursals through PM GatiShakti portal."
    },
    {
        "id": "RULE_VENDOR_DISPUTE_ESCALATION",
        "name": "Contractor Dispute / Arbitration Risk",
        "condition": "dispute_count >= 2 or contractor_rating <= 4.0",
        "severity": "HIGH",
        "category": "Contractual",
        "prescription": "Invoke Conciliation Committee under Vivad Se Vishwas II scheme to resolve claims before formal litigation freezes works."
    },
    {
        "id": "RULE_FOREST_CLEARANCE_PENDING",
        "name": "Stage-II Environmental/Forest Clearance Delay",
        "condition": "forest_clearance_status == 'Pending' and elapsed_time_pct >= 30.0",
        "severity": "MEDIUM",
        "category": "Regulatory",
        "prescription": "Engage MoEFCC regional empowered committee for fast-track Stage-II approval and compensatory afforestation land mutation."
    },
    {
        "id": "RULE_COST_OVERRUN_PREDICTED",
        "name": "AI Predicted Significant Escalation",
        "condition": "predicted_cost_overrun_pct >= 25.0",
        "severity": "CRITICAL",
        "category": "Predictive",
        "prescription": "Notify IPMD/MoSPI & Cabinet Secretariat for capex reallocation and design optimization prior to revised cost estimate (RCE) submission."
    }
]
