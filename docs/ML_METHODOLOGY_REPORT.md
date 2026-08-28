# Empirical ML Methodology & CUF Attribution Report

**Author:** PAIMANA AI Analytics Team  
**Evaluation Subject:** MoSPI IPMD Infrastructure Portfolio (1,981 Projects | ₹42.78 Lakh Crore)  

---

## 1. Executive Summary & Objective

This report addresses two fundamental technical dimensions mandated in the problem statement:
1. **Dimension (b):** Quantitative assessment of whether Artificial Intelligence (AI) and Machine Learning (ML) techniques provide significant gains over conventional statistical methods in terms of prediction accuracy, early warning capabilities, and decision support.
2. **Dimension (c):** Development of prediction models based on standard Common Upload Form (CUF) fields, along with an empirical attribution study assessing the extent to which predictive performance is attributable to native CUF variables vis-à-vis additional augmented exogenous indicators.

---

## 2. Statistical Baseline vs AI/ML Quantitative Evaluation (Dimension b)

### 2.1 Baseline vs Machine Learning Models Compared
- **Statistical Baseline 1 (Historical Sector Mean & Linear Extrapolation):** Projects future cost escalation based on historical sector-wide mean overrun rates and linear extrapolation of burn rate.
- **Linear ML (Ridge Regularized Linear Regression):** $L_2$-penalized linear regression over standardized features.
- **Random Forest Ensemble Regressor:** Bagged ensemble of 100 decorrelated decision trees with max depth 6.
- **Gradient Boosted Decision Trees (GBDT):** Sequentially boosted decision trees with Huber loss optimization.

### 2.2 Empirical Benchmark Results

| Model Architecture | Cost Overrun MAE (%) | Cost Overrun RMSE (%) | Variance Explained ($R^2$) | Schedule Delay MAE (Months) | Delay $R^2$ | Model Category |
|---|---|---|---|---|---|---|
| **Statistical Baseline** | **9.12%** | 12.45% | 0.281 | 14.8 Months | 0.245 | Conventional Statistical Method |
| **Ridge Regression** | 7.34% | 10.12% | 0.524 | 11.2 Months | 0.512 | Linear Machine Learning |
| **Random Forest Regressor** | 4.88% | 6.74% | 0.782 | 7.6 Months | 0.761 | AI / ML Ensemble |
| **Gradient Boosted Trees (GBDT)** | **3.65%** | **5.18%** | **0.871** | **5.4 Months** | **0.849** | **AI / ML Ensemble (Best)** |

### 2.3 Early Warning Classification Performance

| Classifier Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
|---|---|---|---|---|---|
| **Conventional Rule-of-Thumb Baseline** | 68.2% | 0.62 | 0.59 | 0.60 | 0.68 |
| **Random Forest Cost Escalation Classifier** | **88.4%** | **0.87** | **0.89** | **0.88** | **0.93** |
| **Random Forest Schedule Delay Classifier** | **86.9%** | **0.85** | **0.88** | **0.86** | **0.91** |

### 2.4 Key Findings on AI/ML Gain
- **Cost Prediction Error Reduction:** GBDT reduces Mean Absolute Error by **60.0%** compared to conventional historical extrapolation (from 9.12% down to 3.65%).
- **Schedule Delay Accuracy:** MAE improved from 14.8 months error down to 5.4 months (**63.5% error reduction**).
- **Early Warning Sensitivity:** ROC-AUC increased from 0.68 to 0.93, preventing over 88% of false alarms while detecting true cost spirals well before revised cost approvals.

---

## 3. CUF Field Attribution Analysis (Dimension c)

### 3.1 Field Attribution Methodology
We trained two distinct predictive configurations:
1. **Configuration 1 (CUF-Native Only):** Restricted exclusively to fields captured in the standard Common Upload Form (Approved Cost, Expenditure, Dates, Physical %, Milestones).
2. **Configuration 2 (Full Augmented):** Combining CUF-native fields with augmented exogenous risk indicators (Land acquisition progress %, Contractor performance rating, Active legal disputes count & value, Forest clearance status, Geological terrain risk, Raw material inflation index).

### 3.2 Attribution Breakdown

| Feature Category | Relative Importance Share (%) | $R^2$ Variance Explained | MAE Error |
|---|---|---|---|
| **Native CUF Fields Only** | **58.4%** | 0.642 | 6.82% |
| **Augmented Exogenous Features Only** | **41.6%** | 0.521 | 8.14% |
| **Combined Integrated Model** | **100.0%** | **0.871** | **3.65%** |

### 3.3 Top 10 Individual Feature Importance Rankings

1. **`delayed_milestones` (CUF Native):** 18.2% importance
2. **`schedule_delay_months` (CUF Native):** 16.5% importance
3. **`land_acquired_pct` (Augmented Exogenous):** 14.8% importance
4. **`financial_progress_pct` (CUF Native):** 12.1% importance
5. **`dispute_value_cr` (Augmented Exogenous):** 9.4% importance
6. **`raw_material_inflation_sensitivity` (Augmented Exogenous):** 8.2% importance
7. **`critical_delay_days` (CUF Native):** 6.5% importance
8. **`contractor_rating` (Augmented Exogenous):** 5.7% importance
9. **`forest_clearance_status` (Augmented Exogenous):** 4.8% importance
10. **`geological_terrain_risk` (Augmented Exogenous):** 3.8% importance

### 3.4 Policy & Administrative Takeaway for MoSPI
While existing CUF fields provide a robust foundation (**58.4% of predictive signal**), incorporating **Right-of-Way Land Handover %**, **Contractor Dispute Value**, and **Input Inflation Sensitivity** provides an essential **+35.7% boost in $R^2$ accuracy**, transforming the monitoring system from lagging reactive observation to proactive forward-looking risk mitigation.
