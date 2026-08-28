# Technical Architecture Whitepaper: PAIMANA AI

**System:** AI-Powered Predictive Analytics and Early Warning Decision Support System  
**Nodal Authority:** Infrastructure & Project Monitoring Division (IPMD), Ministry of Statistics and Programme Implementation (MoSPI), Government of India  
**Target Domain:** Central Sector Infrastructure Projects (₹150 Crore and above)  

---

## 1. System Overview & Problem Formulation

The Infrastructure & Project Monitoring Division (IPMD) monitors mega infrastructure investments across **17 Central Ministries** and **22 infrastructure sectors**. Across nearly two decades, monitoring transitioned from the historical **Online Computerised Monitoring System (OCMS)** to the modernized **Project Assessment, Infrastructure Monitoring and Analytics for Nation-building (PAIMANA)** portal.

As of April 2026, the portfolio comprises:
- **1,981 Monitored Infrastructure Projects**
- **Original Approved Capex:** ₹37.13 Lakh Crore
- **Current Revised Capex:** ₹42.78 Lakh Crore (Cumulative escalation: ₹5.65 Lakh Crore / +15.2%)
- **Cumulative Expenditure:** ₹20.36 Lakh Crore

This platform transitions project monitoring from descriptive periodic reporting into an **AI-driven Predictive and Prescriptive Decision Support System**.

---

## 2. Multi-Tier System Architecture

```
                    ┌────────────────────────────────────────────────────────┐
                    │               PAIMANA & OCMS DATA REPOSITORY           │
                    │   1,981 Projects | ₹42.78 Lakh Cr | 17 Ministries       │
                    └──────────────────────────┬─────────────────────────────┘
                                               │
               ┌───────────────────────────────┴───────────────────────────────┐
               ▼                                                               ▼
┌──────────────────────────────┐                              ┌──────────────────────────────┐
│  CUF Schema Ingestion Layer  │                              │   Augmented Feature Store    │
│  (Cost, Dates, Exp, Physical)│                              │ (Land, Contractor, Disputes) │
└──────────────┬───────────────┘                              └──────────────┬───────────────┘
               │                                                             │
               └───────────────────────────────┬─────────────────────────────┘
                                               ▼
               ┌───────────────────────────────────────────────────────────────┐
               │              AI / ML PREDICTIVE ANALYTICS ENGINE              │
               ├───────────────────────────────┬───────────────────────────────┤
               │ • Cost Overrun GBDT Regressor │ • Schedule Delay Regressor    │
               │ • Cost Escalation Classifier  │ • Delay Risk Classifier       │
               │ • Statistical Baseline Matrix │ • CUF Feature Attribution     │
               └───────────────────────────────┬───────────────────────────────┘
                                               │
               ┌───────────────────────────────┴───────────────────────────────┐
               ▼                                                               ▼
┌──────────────────────────────┐                              ┌──────────────────────────────┐
│  Composite Risk Index (PRSF) │                              │ Early Warning Alert Engine   │
│  - Financial / Burn Rate     │                              │ - 60-day Milestone Trigger   │
│  - Milestone & Critical Path │                              │ - Expenditure Mismatch Alert │
│  - Regulatory & Land Acc.    │                              │ - Prescriptive Action Memo   │
│  - Contractor & Operational  │                              │ - Automated Escalation Matrix│
└──────────────┬───────────────┘                              └──────────────┬───────────────┘
               │                                                             │
               └───────────────────────────────┬─────────────────────────────┘
                                               ▼
               ┌───────────────────────────────────────────────────────────────┐
               │              FASTAPI REST API & WEBSOCKET BACKEND             │
               └───────────────────────────────┬───────────────────────────────┘
                                               ▼
               ┌───────────────────────────────────────────────────────────────┐
               │        HIGH-AESTHETIC INTERACTIVE EXECUTIVE COCKPIT & UI       │
               ├───────────────────────────────────────────────────────────────┤
               │ • Executive National Cockpit & Sector Benchmarking Matrix     │
               │ • Pan-India Geo-Spatial Risk Surveillance Map                 │
               │ • Project 360° Explorer & Planned vs Actual S-Curve           │
               │ • Interactive What-If Scenario Sandbox                        │
               │ • CUF Ingestion & Automated AI Schema Compliance Auditor      │
               │ • LLM-Enabled Project Intelligence Assistant ("PAIMANA AI")   │
               └───────────────────────────────────────────────────────────────┘
```

---

## 3. Mathematical & Algorithmic Formulations

### 3.1 Project Risk Scoring Framework (PRSF)
The Composite Project Risk Index $R_{\text{composite}} \in [0, 100]$ is computed as a weighted multi-criteria formulation across five statutory risk vectors:

$$R_{\text{composite}} = 0.25 \cdot R_{\text{financial}} + 0.25 \cdot R_{\text{schedule}} + 0.20 \cdot R_{\text{regulatory}} + 0.15 \cdot R_{\text{contractor}} + 0.15 \cdot R_{\text{macro}}$$

Where:
1. **$R_{\text{financial}}$ (Financial Risk Vector):**
   $$R_{\text{financial}} = 0.55 \cdot \min\left(100, 3.0 \cdot \max(0, P_{\text{financial}} - P_{\text{physical}})\right) + 0.45 \cdot \min\left(100, 2.5 \cdot \Delta C_{\%}\right)$$
2. **$R_{\text{schedule}}$ (Milestone & Schedule Risk Vector):**
   $$R_{\text{schedule}} = 0.40 \cdot \min\left(100, 1.8 \cdot \frac{D_{\text{delay}}}{D_{\text{planned}}}\right) + 0.35 \cdot \min\left(100, 1.5 \cdot \frac{M_{\text{delayed}}}{M_{\text{total}}}\right) + 0.25 \cdot \min\left(100, \frac{D_{\text{critical\_days}}}{180} \cdot 100\right)$$
3. **$R_{\text{regulatory}}$ (Right-of-Way & Statutory Clearance Vector):**
   $$R_{\text{regulatory}} = 0.65 \cdot (100 - P_{\text{land}}) \cdot \alpha + 0.35 \cdot S_{\text{forest}}$$
4. **$R_{\text{contractor}}$ (Contractor Performance & Litigation Vector):**
   $$R_{\text{contractor}} = 0.50 \cdot (10 - Q_{\text{rating}}) \cdot 11.0 + 0.50 \cdot \min\left(100, N_{\text{disputes}} \cdot 28 + \frac{V_{\text{disputes}}}{C_{\text{orig}}} \cdot 150\right)$$
5. **$R_{\text{macro}}$ (Geographical Terrain, Monsoon & Inflation Vector):**
   $$R_{\text{macro}} = 0.40 \cdot T_{\text{terrain}} + 0.30 \cdot I_{\text{monsoon}} \cdot 100 + 0.30 \cdot I_{\text{inflation}} \cdot 100$$

### 3.2 S-Curve Trajectory Modeling
The planned capex curve $C_{\text{planned}}(t)$ is modeled using a Generalized Logistic Sigmoidal formulation:

$$C_{\text{planned}}(t) = \frac{C_{\text{original}}}{1 + \exp\left(-\left(\frac{t}{D_{\text{planned}}} \cdot 6 - 3\right)\right)}$$

The AI-predicted completion trajectory $C_{\text{predicted}}(t)$ extrapolates future disbursements conditioned on remaining duration $\Delta t_{\text{rem}}$ and projected revised cost $C_{\text{revised}}$:

$$C_{\text{predicted}}(t) = C_{\text{actual}}(t_{\text{elapsed}}) + \left(C_{\text{revised}} - C_{\text{actual}}(t_{\text{elapsed}})\right) \cdot \left(\frac{t - t_{\text{elapsed}}}{D_{\text{revised}} - t_{\text{elapsed}}}\right)^{1.3}$$

---

## 4. Machine Learning & Predictive Modeling

1. **Cost Overrun Regressor:** Gradient Boosted Decision Trees (GBDT) with Huber loss robust to fat-tailed infrastructure cost distributions.
2. **Schedule Delay Regressor:** GBDT predicting slippage in months.
3. **Cost Escalation Classifier:** Random Forest Classifier predicting probability of critical budget overrun ($>15\%$).
4. **Schedule Delay Classifier:** Random Forest Classifier predicting probability of major commissioning postponement ($>6\text{ months}$).

---

## 5. Early Warning Alert System (EWAS) & Escalation Matrix

| Trigger Code | Condition | Severity | Escalation Recipient | Prescribed Policy Intervention |
|---|---|---|---|---|
| `RULE_CRITICAL_MILESTONE` | $\frac{M_{\text{delayed}}}{M_{\text{total}}} \ge 0.33 \lor D_{\text{crit}} \ge 60\text{d}$ | **CRITICAL** | Secretary (MoSPI & Line Ministry) | Mandate joint review committee with EPC contractor; order 24/7 double-shift recovery schedule. |
| `RULE_BURN_RATE_MISMATCH` | $P_{\text{fin}} - P_{\text{phys}} \ge 20\% \land P_{\text{phys}} < 50\%$ | **CRITICAL** | Financial Adviser & CAG Auditor | Depute special CAG/PMC audit team to verify site measurement books; freeze unverified advance disbursements. |
| `RULE_LAND_ACQUISITION_STALL` | $P_{\text{land}} < 80\% \land t_{\text{elapsed}} \ge 40\%$ | **HIGH** | State Chief Secretary & DM Taskforce | Escalate to State Apex RoW Taskforce; leverage PM GatiShakti portal for Section 19 land award disbursals. |
| `RULE_VENDOR_DISPUTE_ESCALATION` | $N_{\text{disputes}} \ge 2 \lor Q_{\text{rating}} \le 4.0$ | **HIGH** | Ministry Dispute Resolution Board | Invoke Conciliation Committee under Vivad Se Vishwas II scheme to resolve claims before arbitration freezes works. |
| `RULE_COST_OVERRUN_PREDICTED` | $\widehat{\Delta C_{\%}} \ge 25\%$ | **CRITICAL** | Cabinet Secretariat & IPMD Directorate | Issue early warning notice to IPMD Project Review Division; initiate Value Engineering review prior to RCE approval. |
