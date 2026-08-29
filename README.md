# PAIMANA AI: Predictive Analytics & Early Warning System for Infrastructure Monitoring

**Theme:** AI for Infrastructure Monitoring
**Nodal Authority:** Infrastructure & Project Monitoring Division (IPMD), MoSPI
**Scope:** Central Sector Infrastructure Projects costing ₹150 Crore and above

## 🏛️ Overview

**PAIMANA AI** is an AI/ML-powered infrastructure monitoring and decision-support system designed to help identify **cost overruns, schedule delays, financial risks, and implementation bottlenecks** at an early stage.

The system transforms traditional periodic project monitoring into a **predictive, risk-based, and prescriptive monitoring platform**.

## 🚀 Key Features

### 1. Cost & Time Overrun Prediction

* Predicts cost escalation, absolute overrun, schedule slippage, and delay probability.
* Uses **GBDT, Random Forest, and Ridge Regression**.
* Compares ML predictions against conventional statistical baselines.

### 2. Project Risk Scoring

Generates a **0–100 Composite Risk Score** using five dimensions:

* Financial Risk – 25%
* Schedule & Milestone Risk – 25%
* Regulatory & Land Risk – 20%
* Contractor & Execution Risk – 15%
* Macro & Environmental Risk – 15%

### 3. Early Warning System

Automatically detects:

* Milestone delays
* Financial burn-rate mismatches
* Land acquisition bottlenecks
* Contractor and regulatory risks

It also provides **actionable policy recommendations** based on risk severity.

### 4. What-If Simulation

Policymakers can modify factors such as:

* Land handover percentage
* Schedule delays
* Material price increases
* Contractor disputes

The system instantly recalculates **project risk and predicted overruns**.

### 5. CUF & AI Risk Audit

Analyzes Common Upload Form (CUF) data and evaluates the contribution of project-level and external risk factors using feature importance techniques.

### 6. Interactive Dashboard

A dark, executive-style dashboard featuring:

* Pan-India project risk map
* Project 360° view
* S-curves and analytics
* Risk dashboards
* Alert triage board
* What-If simulator

### 7. PAIMANA AI Assistant

An LLM-powered assistant that enables natural-language queries across project data and generates **executive escalation briefs**.

## 🏗️ Technology Stack

**Backend:** Python, FastAPI, Pandas, NumPy, Scikit-Learn
**Frontend:** HTML, CSS, JavaScript, Chart.js, Leaflet/SVG
**AI/ML:** GBDT, Random Forest, Ridge Regression, Feature Importance
**Architecture:** REST APIs + Interactive Web Dashboard

## 📂 Repository Structure

```text
sih/
├── backend/
│   ├── models/          # ML, Risk, EWAS & AI modules
│   ├── routes/          # Analytics, Projects, Predictions & Alerts
│   ├── app.py
│   └── data_generator.py
├── frontend/
│   ├── index.html
│   ├── css/
│   └── js/
├── docs/
├── run_server.py
├── requirements.txt
└── README.md
```

## ⚡ Quick Start

```bash
cd sih
python -m pip install -r requirements.txt
python run_server.py
```

Open:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## 📊 Key Outcomes

* Predictive **cost and schedule forecasting**
* Automated **project risk scoring**
* Early identification of **implementation bottlenecks**
* **What-If policy simulation**
* AI-powered **project intelligence and recommendations**
* Executive **monitoring dashboard**

## 🛡️ License

Built using open-source technologies for the **Smart India Hackathon (SIH)**.
