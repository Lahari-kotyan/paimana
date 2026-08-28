"""
PAIMANA & OCMS High-Fidelity Infrastructure Projects Data Engine
Generates and manages 1,981 realistic Central Sector Infrastructure Projects (>= ₹150 Cr)
Calibrated to MoSPI IPMD's April 2026 aggregates:
- Total Original Cost: ~₹37.13 Lakh Cr
- Total Revised Cost: ~₹42.78 Lakh Cr
- Total Cumulative Expenditure: ~₹20.36 Lakh Cr
"""

import json
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.config import (
    TOTAL_PROJECTS,
    TARGET_ORIGINAL_COST_LAKH_CR,
    TARGET_REVISED_COST_LAKH_CR,
    TARGET_CUMULATIVE_EXP_LAKH_CR,
    MIN_PROJECT_COST_CR,
    MINISTRIES,
    SECTORS,
    STATES,
    DATA_DIR
)


# Realistic Project Name Templates by Sector
PROJECT_TEMPLATES = {
    "SEC_HWY": [
        ("Delhi-Mumbai Expressway Package {pkg} ({loc1}-{loc2} Section)", "NHAI"),
        ("Bharatmala Pariyojana 4/6-Lane Corridor from {loc1} to {loc2}", "NHAI"),
        ("National Highway NH-{num} Widening & Bypass at {loc1}", "MoRTH"),
        ("Trans-Himalayan Highway Multi-Lane Tunnel & Approach Roads near {loc1}", "NHIDCL"),
        ("Greenfield Coastal Corridor Expressway ({loc1}-{loc2} Phase {phase})", "NHAI"),
        ("Economic Corridor NH-{num} 6-Lane Access Controlled Highway ({loc1})", "NHAI")
    ],
    "SEC_RLY": [
        ("Dedicated Freight Corridor (Western/Eastern Phase-{phase}) near {loc1}", "DFCCIL"),
        ("New Broad Gauge Rail Link {loc1} to {loc2} with Major Bridges", "RVNL"),
        ("High-Speed Rail Bullet Train Section {pkg} ({loc1}-{loc2})", "NHSRCL"),
        ("Railway Doubling & Electrification of {loc1}-{loc2} Section ({num} km)", "CORE"),
        ("Himalayan Strategic Rail Network Rail Tunnel Complex near {loc1}", "IRCON"),
        ("Modern Multimodal Railway Terminal & Station Redevelopment at {loc1}", "RLDA")
    ],
    "SEC_PET": [
        ("Cross-Country Natural Gas Pipeline Grid ({loc1} to {loc2})", "GAIL"),
        ("Integrated Petroleum Refinery Expansion & Polypropylene Unit at {loc1}", "IOCL"),
        ("Strategic Petroleum Reserve Underground Rock Caverns at {loc1}", "ISPRL"),
        ("Green Hydrogen & Bio-Ethanol Mega Plant at {loc1}", "BPCL"),
        ("Crude Oil Pipeline Augmented Pumping Infrastructure at {loc1}", "HPCL")
    ],
    "SEC_PWR_TR": [
        ("765kV High Voltage Direct Current (HVDC) Inter-Regional Grid ({loc1}-{loc2})", "PGCIL"),
        ("Green Energy Corridor Intra-State Transmission Scheme Phase-{phase} in {loc1}", "POWERGRID"),
        ("Substation Automation & GIS Grid Augmentation at {loc1}", "PGCIL")
    ],
    "SEC_PWR_GEN": [
        ("Ultra Mega Supercritical Thermal Power Project ({num}x800 MW) at {loc1}", "NTPC"),
        ("Pumped Storage Hydroelectric Power Facility ({num} MW) in {loc1}", "NHPC"),
        ("Subansiri/Tehri Stage-II Hydroelectric Dam & Powerhouse ({loc1})", "SJVN")
    ],
    "SEC_REN": [
        ("Ultra Mega Solar Park ({num} MW) with Battery Storage at {loc1}", "SECI"),
        ("Offshore & Onshore Hybrid Wind-Solar Power Hub in {loc1}", "NTPC-REL"),
        ("Green Ammonia & Hydrogen Renewable Energy Island at {loc1}", "SECI")
    ],
    "SEC_COAL": [
        ("Open Cast Coal Mining Project ({num} MTPA) with High-Capacity Conveyors at {loc1}", "CIL"),
        ("Mechanized Coal Washery & Pithead Rail Dispatch Facility ({loc1})", "BCCL"),
        ("Coal Bed Methane & Deep Underground Extraction Unit at {loc1}", "NCDC")
    ],
    "SEC_METRO": [
        ("Metro Rail Project Phase-{phase} (Elevated & Underground Corridor {loc1}-{loc2})", "Metro Rail Corp"),
        ("Regional Rapid Transit System (RRTS) Semi High-Speed Line ({loc1}-{loc2})", "NCRTC"),
        ("Urban Light Rail Transit / MetroLite System for {loc1} Smart City", "Metro Rail Corp")
    ],
    "SEC_PORT": [
        ("Greenfield Deep-Water Major Port & Container Terminal Phase-{phase} at {loc1}", "Port Authority"),
        ("Port Connectivity Dedicated Rail-Sea Multimodal Corridor at {loc1}", "Sagarmala Dev"),
        ("LNG Import Terminal & Marine Jetty Infrastructure at {loc1}", "Petronet")
    ],
    "SEC_AIR": [
        ("Greenfield International Airport Terminal-{num} & Parallel Runway at {loc1}", "AAI"),
        ("Regional Airport Modernization & Runway Extension under UDAN at {loc1}", "AAI"),
        ("Air Cargo Hub & Aircraft Maintenance Repair Overhaul (MRO) at {loc1}", "AAI")
    ],
    "SEC_STEEL": [
        ("Integrated Steel Plant Modernization & Pelletization Unit at {loc1}", "SAIL"),
        ("Specialty Alloy & Hot Rolled Coil Expansion Facility at {loc1}", "RINL")
    ],
    "SEC_TEL": [
        ("BharatNet Rural Optical Fiber Network Phase-{phase} across {loc1}", "BBNL"),
        ("National 5G High-Density Core Network Infrastructure in {loc1}", "BSNL")
    ],
    "SEC_ATOM": [
        ("Pressurized Heavy Water Reactor Nuclear Power Unit ({num}x700 MWe) at {loc1}", "NPCIL"),
        ("Fast Breeder Reactor & Reprocessing Facility at {loc1}", "BHAVINI")
    ],
    "SEC_WATER": [
        ("Urban 24x7 Water Supply & Advanced Smart Grid Pipeline in {loc1}", "Jal Nigam"),
        ("Comprehensive Sewage Treatment & River Cleaning Mission at {loc1}", "NMCG")
    ],
    "SEC_IRR": [
        ("National River Interlinking Canal & Barrage System ({loc1}-{loc2})", "NWDA"),
        ("Lift Irrigation & Pressurized Piped Distribution Network in {loc1}", "WRD")
    ],
    "SEC_CHEM": [
        ("Coal-Gasification Based Urea & Fertilizer Complex at {loc1}", "FCIL"),
        ("Petrochemical Derivative & Polymer Manufacturing Unit at {loc1}", "HURL")
    ],
    "SEC_MINE": [
        ("Strategic Rare Earth & Bauxite Mining Complex at {loc1}", "NALCO"),
        ("Copper Ore Underground Mine Expansion Project in {loc1}", "HCL")
    ],
    "SEC_HEALTH": [
        ("All India Institute of Medical Sciences (AIIMS) 750-Bed Super-Specialty Campus at {loc1}", "MoHFW/HSCC"),
        ("National Centre for Disease Control & Bio-Safety Level 4 Lab at {loc1}", "MoHFW")
    ],
    "SEC_LOG": [
        ("Multimodal Logistics Park (MMLP) with Inland Container Depot at {loc1}", "NHLML"),
        ("Central Freight Logistics & Cold Chain Infrastructure Hub at {loc1}", "CONCOR")
    ],
    "SEC_HEAVY": [
        ("Heavy Electrical Equipment & Gas Turbine Manufacturing Facility at {loc1}", "BHEL"),
        ("Heavy Machine Tools & Engineering Foundry Unit in {loc1}", "HMT")
    ],
    "SEC_INLAND": [
        ("National Waterway NW-{num} Multimodal Navigation Terminal at {loc1}", "IWAI"),
        ("Fairway Development & River Ro-Ro Terminal Facility in {loc1}", "IWAI")
    ],
    "SEC_SMART": [
        ("Industrial Smart City & Integrated Manufacturing Node at {loc1}", "NICDC"),
        ("Special Investment Region Trunk Infrastructure & Utilities at {loc1}", "Dholera/DMIC")
    ]
}

CITY_NAMES = {
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Solapur", "Thane"],
    "Uttar Pradesh": ["Varanasi", "Gorakhpur", "Lucknow", "Kanpur", "Ayodhya", "Prayagraj", "Noida"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Salem", "Tiruchirappalli", "Tuticorin"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Kandla", "Bhavnagar", "Jamnagar"],
    "Karnataka": ["Bengaluru", "Mysuru", "Hubballi", "Mangaluru", "Belagavi", "Kalaburagi"],
    "Madhya Pradesh": ["Indore", "Bhopal", "Gwalior", "Jabalpur", "Ujjain", "Singrauli"],
    "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Tirupati", "Guntur", "Kakinada"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Kota", "Bikaner", "Udaipur", "Barmer"],
    "West Bengal": ["Kolkata", "Siliguri", "Asansol", "Durgapur", "Haldia", "Kharagpur"],
    "Odisha": ["Bhubaneswar", "Paradip", "Rourkela", "Cuttack", "Jharsuguda", "Angul"],
    "Bihar": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Darbhanga", "Barauni"],
    "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Ramagundam", "Karimnagar"],
    "Kerala": ["Kochi", "Thiruvananthapuram", "Kozhikode", "Kannur", "Kollam"],
    "Jharkhand": ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Deoghar"],
    "Assam": ["Guwahati", "Dibrugarh", "Silchar", "Jorhat", "Bongaigaon"],
    "Haryana": ["Gurugram", "Faridabad", "Panipat", "Ambala", "Hisar", "Rohtak"],
    "Punjab": ["Amritsar", "Ludhiana", "Jalandhar", "Bathinda", "Patiala"],
    "Chhattisgarh": ["Raipur", "Bhilai", "Bilaspur", "Korba", "Jagdalpur"],
    "Jammu & Kashmir": ["Srinagar", "Jammu", "Udhampur", "Baramulla", "Anantnag"],
    "Uttarakhand": ["Dehradun", "Haridwar", "Rishikesh", "Karnaprayag", "Haldwani"],
    "Himachal Pradesh": ["Shimla", "Manali", "Dharamshala", "Solan", "Mandi"],
    "Delhi NCR": ["New Delhi", "Dwarka", "IGI Airport", "Anand Vihar", "Rohini"],
    "Goa": ["Panaji", "Mormugao", "Margao", "Mopa"],
    "Arunachal Pradesh": ["Itanagar", "Tawang", "Pasighat", "Ziro"],
    "Meghalaya": ["Shillong", "Tura", "Jowai"],
    "Manipur": ["Imphal", "Churachandpur", "Thoubal"],
    "Tripura": ["Agartala", "Udaipur", "Dharmanagar"],
    "Nagaland": ["Kohima", "Dimapur", "Mokokchung"],
    "Mizoram": ["Aizawl", "Lunglei", "Champhai"],
    "Sikkim": ["Gangtok", "Namchi", "Pakyong"],
    "Multi-State / National": ["National Corridor", "Inter-State Hub", "Pan-India Grid"]
}

def generate_paimana_dataset(num_projects: int = TOTAL_PROJECTS, seed: int = 42) -> pd.DataFrame:
    """
    Generates a full, realistic PAIMANA / OCMS dataset with exactly 1,981 infrastructure projects
    meeting the MoSPI April 2026 portfolio benchmarks.
    """
    np.random.seed(seed)
    random.seed(seed)
    
    records = []
    
    # State weights for random sampling
    state_names = list(STATES.keys())
    state_weights = [STATES[s]["projects_wt"] for s in state_names]
    state_weights = np.array(state_weights) / sum(state_weights)
    
    # Sector dictionary lookup
    sector_map = {s["id"]: s for s in SECTORS}
    sector_ids = [s["id"] for s in SECTORS]
    
    # Target total capex in Cr
    target_original_total = TARGET_ORIGINAL_COST_LAKH_CR * 100000.0  # 3,713,000 Cr
    
    # Sample base costs from a log-normal distribution (infrastructure projects follow power-law / log-normal)
    raw_costs = np.random.lognormal(mean=7.0, sigma=0.95, size=num_projects)
    raw_costs = np.clip(raw_costs, MIN_PROJECT_COST_CR, 85000.0)
    # Scale to match exact target total capex
    scaled_original_costs = raw_costs * (target_original_total / np.sum(raw_costs))
    
    # Sector cost weights adjustment
    for i in range(num_projects):
        # Pick state
        state = np.random.choice(state_names, p=state_weights)
        state_meta = STATES[state]
        
        # Pick sector
        sec_id = random.choice(sector_ids)
        sec_meta = sector_map[sec_id]
        
        orig_cost = max(MIN_PROJECT_COST_CR, round(float(scaled_original_costs[i]), 2))
        
        # Project Dates (Between 2014 and 2029)
        start_year = random.randint(2014, 2023)
        start_month = random.randint(1, 12)
        start_day = random.randint(1, 28)
        start_date = datetime(start_year, start_month, start_day)
        
        # Original planned duration (months): depends on cost & sector
        planned_duration_months = int(np.clip(18 + (orig_cost / 150.0) * 1.2 + random.randint(-6, 12), 18, 120))
        orig_doc = start_date + timedelta(days=int(planned_duration_months * 30.4))
        
        # Current timeline progress
        reference_date = datetime(2026, 4, 15)  # April 2026 PAIMANA Snapshot
        total_planned_days = max(1, (orig_doc - start_date).days)
        elapsed_days = max(1, (reference_date - start_date).days)
        elapsed_time_pct = min(150.0, round((elapsed_days / total_planned_days) * 100.0, 1))
        
        # Risk factors & External drivers (Synthetic realistic ground truth)
        land_required = round(float(np.random.uniform(50.0, 1800.0)), 1)
        # Land acquisition depends on state and sector
        if sec_meta["delay_risk"] > 0.6:
            land_acquired_pct = round(float(np.random.beta(4, 2) * 100), 1)
        else:
            land_acquired_pct = round(float(np.random.beta(7, 2) * 100), 1)
            
        forest_status_choices = ["Approved", "Stage-I", "Stage-II Pending", "Exempted"]
        forest_weights = [0.65, 0.15, 0.12, 0.08]
        forest_clearance = np.random.choice(forest_status_choices, p=forest_weights)
        
        contractor_rating = round(float(np.random.uniform(3.2, 9.8)), 1)
        dispute_count = np.random.choice([0, 1, 2, 3, 4], p=[0.55, 0.25, 0.12, 0.05, 0.03])
        dispute_value = round(dispute_count * float(np.random.uniform(15.0, 350.0)), 2)
        
        terrain_choices = ["Low/Plains", "Moderate/Plateau", "High/Himalayan/Riverine"]
        if state_meta["region"] in ["North-East", "North"]:
            terrain_risk = np.random.choice(terrain_choices, p=[0.3, 0.35, 0.35])
        else:
            terrain_risk = np.random.choice(terrain_choices, p=[0.6, 0.3, 0.1])
            
        monsoon_vuln = round(float(np.random.uniform(0.1, 0.95)), 2)
        material_inflation_sens = round(float(np.random.uniform(0.2, 0.9)), 2)
        
        # Milestones
        total_milestones = random.randint(12, 48)
        # Milestones completed
        milestone_completion_rate = min(1.0, max(0.05, (elapsed_time_pct / 100.0) * np.random.uniform(0.65, 1.05)))
        completed_milestones = int(total_milestones * milestone_completion_rate)
        
        # Delay calculation
        delay_prob = sec_meta["delay_risk"]
        is_delayed = (random.random() < delay_prob) or (land_acquired_pct < 75.0) or (dispute_count >= 2)
        
        if is_delayed:
            delay_months = int(np.clip(
                (100.0 - land_acquired_pct) * 0.15 + 
                dispute_count * 4.5 + 
                (1 if forest_clearance == "Stage-II Pending" else 0) * 8 +
                (10.0 - contractor_rating) * 2.0 +
                random.randint(2, 18),
                3, 84
            ))
            delayed_milestones = random.randint(1, max(1, total_milestones - completed_milestones))
            critical_delay_days = delay_months * 30 + random.randint(-15, 45)
        else:
            delay_months = 0
            delayed_milestones = 0
            critical_delay_days = 0
            
        anticipated_doc = orig_doc + timedelta(days=int(delay_months * 30.4))
        
        # Physical progress %
        expected_phys = min(100.0, (elapsed_time_pct * 0.85))
        if delay_months > 0:
            physical_progress = round(float(np.clip(expected_phys * (1.0 - (delay_months / (planned_duration_months + delay_months)) * 0.6) + random.uniform(-4, 4), 5.0, 98.0)), 1)
        else:
            physical_progress = round(float(np.clip(expected_phys + random.uniform(0, 5), 10.0, 100.0)), 1)
            
        # Cost Overrun calculation
        # In infrastructure, cost overruns stem from time delays, material inflation, contractor disputes, land cost escalations
        if delay_months > 0 or physical_progress > 60:
            cost_escalation_pct = max(0.0, round(
                (delay_months * 0.55) + 
                (material_inflation_sens * 8.5) + 
                (dispute_value / (orig_cost + 1)) * 12.0 + 
                (100.0 - land_acquired_pct) * 0.08 +
                (8.0 if terrain_risk == "High/Himalayan/Riverine" else 0.0) +
                random.uniform(-3.5, 6.0), 
                2
            ))
        else:
            cost_escalation_pct = max(0.0, round(random.uniform(0.0, 4.5), 2))
            
        revised_cost = round(orig_cost * (1.0 + cost_escalation_pct / 100.0), 2)
        cost_overrun_cr = round(revised_cost - orig_cost, 2)
        
        # Cumulative expenditure
        # Burn rate can sometimes lead physical progress
        exp_factor = (physical_progress / 100.0) * (1.0 + (cost_escalation_pct / 100.0) * 0.4) + random.uniform(-0.04, 0.08)
        exp_factor = np.clip(exp_factor, 0.05, 1.05)
        cumulative_exp = round(float(min(revised_cost, orig_cost * exp_factor)), 2)
        financial_progress = round(float((cumulative_exp / revised_cost) * 100.0), 1)
        
        # Project Name Generation
        city_list = CITY_NAMES.get(state, ["City-A", "City-B"])
        loc1 = random.choice(city_list)
        loc2 = random.choice([c for c in city_list if c != loc1] or [loc1 + " Ext"])
        templates = PROJECT_TEMPLATES.get(sec_id, [("Infrastructure Scheme at {loc1}", "PSU")])
        tmpl, def_agency = random.choice(templates)
        
        proj_name = tmpl.format(
            loc1=loc1,
            loc2=loc2,
            pkg=random.randint(1, 18),
            phase=random.randint(1, 4),
            num=random.randint(4, 99)
        )
        
        # Project ID format: PAIMANA-SEC-YEAR-XXXX
        proj_id = f"PAIMANA-{sec_meta['id']}-{start_year}-{i+1001}"
        
        # Agency
        agency = def_agency
        
        # Historical OCMS vs Live PAIMANA tag
        data_source = "OCMS_Historical" if start_year <= 2019 else "PAIMANA_Live"
        
        # Status
        if physical_progress >= 99.0:
            status = "Commissioned"
        elif physical_progress >= 85.0:
            status = "Nearing Completion"
        elif delay_months >= 24 and physical_progress < 40.0:
            status = "Stalled/Delayed"
        elif physical_progress >= 30.0:
            status = "Under Implementation"
        else:
            status = "Ongoing"
            
        # Coordinates with realistic jitter
        base_lat = state_meta["lat"] + random.uniform(-0.6, 0.6)
        base_lng = state_meta["lng"] + random.uniform(-0.6, 0.6)
        
        records.append({
            "project_id": proj_id,
            "project_name": proj_name,
            "ministry_code": sec_meta["ministry"],
            "ministry_name": next((m["name"] for m in MINISTRIES if m["code"] == sec_meta["ministry"]), "Central Ministry"),
            "sector_id": sec_meta["id"],
            "sector_name": sec_meta["name"],
            "state": state,
            "region": state_meta["region"],
            "agency_name": agency,
            "location_lat": round(base_lat, 4),
            "location_lng": round(base_lng, 4),
            "original_cost_cr": orig_cost,
            "revised_cost_cr": revised_cost,
            "cost_overrun_cr": cost_overrun_cr,
            "cost_overrun_pct": cost_escalation_pct,
            "cumulative_exp_cr": cumulative_exp,
            "financial_progress_pct": financial_progress,
            "physical_progress_pct": physical_progress,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "original_doc": orig_doc.strftime("%Y-%m-%d"),
            "anticipated_doc": anticipated_doc.strftime("%Y-%m-%d"),
            "planned_duration_months": planned_duration_months,
            "schedule_delay_months": delay_months,
            "elapsed_time_pct": elapsed_time_pct,
            "total_milestones": total_milestones,
            "completed_milestones": completed_milestones,
            "delayed_milestones": delayed_milestones,
            "critical_delay_days": critical_delay_days,
            # Augmented Variables
            "land_required_hectares": land_required,
            "land_acquired_pct": land_acquired_pct,
            "forest_clearance_status": forest_clearance,
            "contractor_rating": contractor_rating,
            "dispute_count": dispute_count,
            "dispute_value_cr": dispute_value,
            "geological_terrain_risk": terrain_risk,
            "monsoon_vulnerability_index": monsoon_vuln,
            "raw_material_inflation_sensitivity": material_inflation_sens,
            "cuf_submission_date": "2026-04-10",
            "data_source": data_source,
            "project_status": status,
            # Target Classification
            "is_high_cost_overrun": 1 if cost_escalation_pct >= 15.0 else 0,
            "is_high_delay": 1 if delay_months >= 6 else 0
        })
        
    df = pd.DataFrame(records)
    
    # Scale revised cost and cumulative expenditure to match MoSPI April 2026 targets precisely
    target_revised_total = TARGET_REVISED_COST_LAKH_CR * 100000.0  # 4,278,000 Cr
    target_exp_total = TARGET_CUMULATIVE_EXP_LAKH_CR * 100000.0      # 2,036,000 Cr
    
    # Adjust overruns to match target revised capex
    current_overrun_sum = (df["revised_cost_cr"] - df["original_cost_cr"]).sum()
    desired_overrun_sum = target_revised_total - target_original_total
    overrun_scale = desired_overrun_sum / max(1.0, current_overrun_sum)
    
    df["cost_overrun_cr"] = (df["cost_overrun_cr"] * overrun_scale).round(2)
    df["revised_cost_cr"] = (df["original_cost_cr"] + df["cost_overrun_cr"]).round(2)
    df["cost_overrun_pct"] = ((df["cost_overrun_cr"] / df["original_cost_cr"]) * 100.0).round(2)
    
    # Adjust cumulative expenditure to match target disbursement
    current_exp_sum = df["cumulative_exp_cr"].sum()
    exp_scale = target_exp_total / max(1.0, current_exp_sum)
    df["cumulative_exp_cr"] = (df["cumulative_exp_cr"] * exp_scale).round(2)
    df["cumulative_exp_cr"] = df[["cumulative_exp_cr", "revised_cost_cr"]].min(axis=1)
    df["financial_progress_pct"] = ((df["cumulative_exp_cr"] / df["revised_cost_cr"]) * 100.0).round(1)
    
    current_orig_total = df["original_cost_cr"].sum()
    current_rev_total = df["revised_cost_cr"].sum()
    current_exp_total = df["cumulative_exp_cr"].sum()
    
    print(f"--- PAIMANA Portfolio Calibration ---")
    print(f"Total Projects: {len(df)}")
    print(f"Original Cost Total: INR {current_orig_total/100000.0:.2f} Lakh Cr (Target: ~INR {TARGET_ORIGINAL_COST_LAKH_CR} Lakh Cr)")
    print(f"Revised Cost Total: INR {current_rev_total/100000.0:.2f} Lakh Cr (Target: ~INR {TARGET_REVISED_COST_LAKH_CR} Lakh Cr)")
    print(f"Cumulative Exp Total: INR {current_exp_total/100000.0:.2f} Lakh Cr (Target: ~INR {TARGET_CUMULATIVE_EXP_LAKH_CR} Lakh Cr)")
    
    return df



def save_paimana_dataset():
    """Generates and saves PAIMANA dataset to JSON and CSV formats."""
    df = generate_paimana_dataset()
    csv_path = DATA_DIR / "paimana_projects_1981.csv"
    json_path = DATA_DIR / "paimana_projects_1981.json"
    
    df.to_csv(csv_path, index=False)
    
    # Save JSON with records orientation
    records = df.to_dict(orient="records")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
        
    print(f"Saved dataset to {csv_path} and {json_path}")
    return df

if __name__ == "__main__":
    save_paimana_dataset()
