# PAIMANA AI User Manual & Operational Guide

**System:** AI-Powered Predictive Analytics & Early Warning Platform  
**Target Users:** MoSPI IPMD Officers, Line Ministry Project Directors, Field Engineers, Decision Makers  

---

## 1. Quick Start & Accessing the Platform

1. **Prerequisites:** Python 3.10+ installed.
2. **Launch System:**
   ```bash
   python run_server.py
   ```
3. **Open Web Browser:** Navigate to `http://127.0.0.1:8000`.

---

## 2. Navigating Dashboard Modules

### 2.1 National Cockpit
- **Executive KPI Cards:** Monitor national capex totals (₹42.78L Cr revised capex, ₹5.65L Cr overrun, 1,981 projects).
- **Sectoral Capex Chart:** Inspect capex distribution across the top 10 infrastructure sectors.
- **Risk Donut:** High-level view of projects in Critical, Moderate, and On-Track risk categories.

### 2.2 Geo-Spatial Risk Surveillance Map
- **Interactive State Pins:** Hover over any state pin to view total capex allocation, project count, and composite risk score.
- **Drill-Down Filtering:** Click on any state pin to automatically filter the Project 360° Explorer table to that specific State/UT.

### 2.3 Project 360° Explorer & Dossier
- **Search & Filters:** Search by Project Name, Project ID (`PAIMANA-HWY-2023-1042`), executing agency, or city. Filter by 17 Ministries, 22 Sectors, or Risk Tier.
- **Click to Open 360° Dossier:**
  - **S-Curve Chart:** Compare planned baseline S-curve, actual cumulative expenditure, and AI-predicted completion path.
  - **5D Risk Radar:** Inspect dimensional scores for Financial, Schedule, Regulatory, Contractor, and Macro risks.
  - **Early Warning Alarms:** Review active stage-gate bottlenecks and root-cause diagnoses.
  - **Generate Memorandum:** Click "📄 Generate MoSPI Escalation Brief" to generate a formal printable memorandum.

### 2.4 What-If Scenario Sandbox
- Select any project from the dropdown.
- Adjust policy & operational levers:
  - **Right-of-Way Land Handover Delta:** Simulate $+10\%$ or $-20\%$ land acquisition changes.
  - **Additional Schedule Delay:** Simulate $+6$ to $+24$ months timeline shifts.
  - **Raw Material Inflation Surge:** Simulate $+5\%$ to $+30\%$ steel/cement price rises.
  - **Contractor Disputes:** Simulate additional legal claims.
- Observe real-time recalculations for Revised Capex, Cost Escalation ₹ Cr, and PRSF Risk Score.

### 2.5 Early Warning Alert Center
- Review the prioritized live feed of active alarms categorized as **CRITICAL**, **HIGH**, or **MEDIUM**.
- Review specific prescriptive actions (e.g. convening joint review committees, third-party technical audits, dispute conciliation).

### 2.6 ML & CUF Benchmarks
- Inspect empirical model evaluation metrics (MAE, RMSE, $R^2$, Accuracy, ROC-AUC) comparing Conventional Statistical Baselines vs AI/ML models.
- Review the **CUF Feature Attribution Donut** and ranked feature importance list.

### 2.7 Common Upload Form (CUF) Pipeline
- Paste monthly JSON submissions or click **"Load Sample CUF Template"**.
- Click **"Execute AI Schema Validation & Risk Audit"** to verify data integrity, detect anomalies, and obtain immediate AI risk assessments.

### 2.8 PAIMANA AI Assistant (LLM Copilot)
- Type natural language queries into the chat input bar or click quick-prompt chips.
- Example queries:
  - *"Which railway projects in Maharashtra have highest cost overrun?"*
  - *"Show me projects delayed due to forest clearance bottlenecks"*
  - *"Summarize critical projects in Power Transmission sector"*
