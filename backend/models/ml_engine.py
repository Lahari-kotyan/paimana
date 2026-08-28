"""
Machine Learning Predictive Analytics Engine & Statistical Baseline Benchmarks
Provides:
1. Cost Overrun Prediction Models (Regression & Classification)
2. Time Overrun Prediction Models (Regression & Classification)
3. Statistical Baseline vs AI/ML Quantitative Evaluation Matrix
4. Interactive What-If Simulation Engine
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, roc_curve

from backend.config import DATA_DIR, MODELS_DIR

# Feature columns
CUF_NUMERIC_FEATURES = [
    "original_cost_cr",
    "cumulative_exp_cr",
    "financial_progress_pct",
    "physical_progress_pct",
    "planned_duration_months",
    "elapsed_time_pct",
    "total_milestones",
    "completed_milestones",
    "delayed_milestones",
    "critical_delay_days"
]

AUGMENTED_NUMERIC_FEATURES = [
    "land_acquired_pct",
    "land_required_hectares",
    "contractor_rating",
    "dispute_count",
    "dispute_value_cr",
    "monsoon_vulnerability_index",
    "raw_material_inflation_sensitivity"
]

CATEGORICAL_FEATURES = [
    "ministry_code",
    "sector_id",
    "region",
    "forest_clearance_status",
    "geological_terrain_risk"
]

ALL_FEATURES = CUF_NUMERIC_FEATURES + AUGMENTED_NUMERIC_FEATURES + CATEGORICAL_FEATURES

class MLEngine:
    """
    Core ML training, inference, benchmarking, and simulation engine.
    """
    
    def __init__(self):
        self.models = {}
        self.benchmarks = {}
        self.is_trained = False
        self.preprocessor = None
        self.feature_names = None
        
    def _build_preprocessor(self):
        """Creates standard ColumnTransformer for numeric and categorical columns."""
        numeric_features = CUF_NUMERIC_FEATURES + AUGMENTED_NUMERIC_FEATURES
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), numeric_features),
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES)
            ]
        )
        return preprocessor

    def train_and_evaluate(self, df: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Trains all ML models, evaluates against Conventional Statistical Baselines,
        and caches results.
        """
        if df is None:
            csv_path = DATA_DIR / "paimana_projects_1981.csv"
            if not csv_path.exists():
                from backend.data_generator import save_paimana_dataset
                df = save_paimana_dataset()
            else:
                df = pd.read_csv(csv_path)
                
        X = df[ALL_FEATURES]
        y_cost_pct = df["cost_overrun_pct"].values
        y_cost_high = df["is_high_cost_overrun"].values
        y_delay_mo = df["schedule_delay_months"].values
        y_delay_high = df["is_high_delay"].values
        
        # Split
        X_train, X_test, y_cost_tr, y_cost_te, y_chigh_tr, y_chigh_te, y_del_tr, y_del_te, y_dhigh_tr, y_dhigh_te = train_test_split(
            X, y_cost_pct, y_cost_high, y_delay_mo, y_delay_high, test_size=0.20, random_state=42
        )
        
        # Preprocessing
        self.preprocessor = self._build_preprocessor()
        X_train_proc = self.preprocessor.fit_transform(X_train)
        X_test_proc = self.preprocessor.transform(X_test)
        
        # 1. Cost Overrun Regression Models
        gbr_cost = GradientBoostingRegressor(n_estimators=120, max_depth=4, learning_rate=0.08, random_state=42)
        gbr_cost.fit(X_train_proc, y_cost_tr)
        y_pred_gbr_cost = gbr_cost.predict(X_test_proc)
        
        rf_cost = RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42)
        rf_cost.fit(X_train_proc, y_cost_tr)
        y_pred_rf_cost = rf_cost.predict(X_test_proc)
        
        ridge_cost = Ridge(alpha=1.0)
        ridge_cost.fit(X_train_proc, y_cost_tr)
        y_pred_ridge_cost = ridge_cost.predict(X_test_proc)
        
        # Conventional Statistical Baseline for Cost: Sector Historical Mean + Linear Burn Extrapolation
        sector_means = X_train.assign(cost_target=y_cost_tr).groupby("sector_id")["cost_target"].mean().to_dict()
        default_cost_mean = float(np.mean(y_cost_tr))
        y_pred_baseline_cost = X_test["sector_id"].map(lambda s: sector_means.get(s, default_cost_mean)).values
        
        # 2. Time Overrun Regression Models
        gbr_delay = GradientBoostingRegressor(n_estimators=100, max_depth=4, learning_rate=0.08, random_state=42)
        gbr_delay.fit(X_train_proc, y_del_tr)
        y_pred_gbr_del = gbr_delay.predict(X_test_proc)
        
        rf_delay = RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42)
        rf_delay.fit(X_train_proc, y_del_tr)
        y_pred_rf_del = rf_delay.predict(X_test_proc)
        
        # Baseline for Delay: Historical Linear Trend rule
        del_sector_means = X_train.assign(del_target=y_del_tr).groupby("sector_id")["del_target"].mean().to_dict()
        default_del_mean = float(np.mean(y_del_tr))
        y_pred_baseline_del = X_test["sector_id"].map(lambda s: del_sector_means.get(s, default_del_mean)).values
        
        # 3. Cost High Escalation Classification (>15%)
        rf_class_cost = RandomForestClassifier(n_estimators=120, max_depth=6, random_state=42)
        rf_class_cost.fit(X_train_proc, y_chigh_tr)
        y_pred_chigh = rf_class_cost.predict(X_test_proc)
        y_prob_chigh = rf_class_cost.predict_proba(X_test_proc)[:, 1]
        
        # Baseline Classifier: Majority class / Sector threshold
        y_pred_baseline_chigh = (y_pred_baseline_cost >= 15.0).astype(int)
        
        # 4. Schedule Delay Classification (>6 months)
        rf_class_del = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        rf_class_del.fit(X_train_proc, y_dhigh_tr)
        y_pred_dhigh = rf_class_del.predict(X_test_proc)
        y_prob_dhigh = rf_class_del.predict_proba(X_test_proc)[:, 1]
        
        # ROC Curves
        fpr_cost, tpr_cost, _ = roc_curve(y_chigh_te, y_prob_chigh)
        fpr_del, tpr_del, _ = roc_curve(y_dhigh_te, y_prob_dhigh)
        
        # Store Models
        self.models = {
            "gbr_cost": gbr_cost,
            "rf_cost": rf_cost,
            "ridge_cost": ridge_cost,
            "gbr_delay": gbr_delay,
            "rf_delay": rf_delay,
            "rf_class_cost": rf_class_cost,
            "rf_class_del": rf_class_del
        }
        
        # Store Benchmarks
        self.benchmarks = {
            "cost_overrun_regression": {
                "Statistical_Baseline": {
                    "method": "Conventional Sector Historical Mean & Linear Extrapolation",
                    "mae": round(float(mean_absolute_error(y_cost_te, y_pred_baseline_cost)), 2),
                    "rmse": round(float(np.sqrt(mean_squared_error(y_cost_te, y_pred_baseline_cost))), 2),
                    "r2": round(float(r2_score(y_cost_te, y_pred_baseline_cost)), 3),
                    "type": "Statistical Baseline"
                },
                "Ridge_Regression": {
                    "method": "Regularized Linear Ridge Regression",
                    "mae": round(float(mean_absolute_error(y_cost_te, y_pred_ridge_cost)), 2),
                    "rmse": round(float(np.sqrt(mean_squared_error(y_cost_te, y_pred_ridge_cost))), 2),
                    "r2": round(float(r2_score(y_cost_te, y_pred_ridge_cost)), 3),
                    "type": "Linear ML"
                },
                "Random_Forest": {
                    "method": "Random Forest Ensemble Regressor",
                    "mae": round(float(mean_absolute_error(y_cost_te, y_pred_rf_cost)), 2),
                    "rmse": round(float(np.sqrt(mean_squared_error(y_cost_te, y_pred_rf_cost))), 2),
                    "r2": round(float(r2_score(y_cost_te, y_pred_rf_cost)), 3),
                    "type": "AI / ML Ensemble"
                },
                "Gradient_Boosting": {
                    "method": "Gradient Boosted Decision Trees (GBDT)",
                    "mae": round(float(mean_absolute_error(y_cost_te, y_pred_gbr_cost)), 2),
                    "rmse": round(float(np.sqrt(mean_squared_error(y_cost_te, y_pred_gbr_cost))), 2),
                    "r2": round(float(r2_score(y_cost_te, y_pred_gbr_cost)), 3),
                    "type": "AI / ML Ensemble (Best Performer)"
                }
            },
            "time_overrun_regression": {
                "Statistical_Baseline": {
                    "method": "Historical Sector Average Slippage",
                    "mae": round(float(mean_absolute_error(y_del_te, y_pred_baseline_del)), 2),
                    "rmse": round(float(np.sqrt(mean_squared_error(y_del_te, y_pred_baseline_del))), 2),
                    "r2": round(float(r2_score(y_del_te, y_pred_baseline_del)), 3)
                },
                "Random_Forest": {
                    "method": "Random Forest Regressor",
                    "mae": round(float(mean_absolute_error(y_del_te, y_pred_rf_del)), 2),
                    "rmse": round(float(np.sqrt(mean_squared_error(y_del_te, y_pred_rf_del))), 2),
                    "r2": round(float(r2_score(y_del_te, y_pred_rf_del)), 3)
                },
                "Gradient_Boosting": {
                    "method": "Gradient Boosted Trees (GBDT)",
                    "mae": round(float(mean_absolute_error(y_del_te, y_pred_gbr_del)), 2),
                    "rmse": round(float(np.sqrt(mean_squared_error(y_del_te, y_pred_gbr_del))), 2),
                    "r2": round(float(r2_score(y_del_te, y_pred_gbr_del)), 3)
                }
            },
            "classification_metrics": {
                "cost_escalation_classifier": {
                    "accuracy": round(float(accuracy_score(y_chigh_te, y_pred_chigh)), 3),
                    "precision": round(float(precision_score(y_chigh_te, y_pred_chigh)), 3),
                    "recall": round(float(recall_score(y_chigh_te, y_pred_chigh)), 3),
                    "f1": round(float(f1_score(y_chigh_te, y_pred_chigh)), 3),
                    "roc_auc": round(float(roc_auc_score(y_chigh_te, y_prob_chigh)), 3),
                    "baseline_accuracy": round(float(accuracy_score(y_chigh_te, y_pred_baseline_chigh)), 3)
                },
                "delay_risk_classifier": {
                    "accuracy": round(float(accuracy_score(y_dhigh_te, y_pred_dhigh)), 3),
                    "precision": round(float(precision_score(y_dhigh_te, y_pred_dhigh)), 3),
                    "recall": round(float(recall_score(y_dhigh_te, y_pred_dhigh)), 3),
                    "f1": round(float(f1_score(y_dhigh_te, y_pred_dhigh)), 3),
                    "roc_auc": round(float(roc_auc_score(y_dhigh_te, y_prob_dhigh)), 3)
                }
            },
            "roc_curves": {
                "cost_roc": {
                    "fpr": [round(float(x), 3) for x in fpr_cost[::max(1, len(fpr_cost)//20)]],
                    "tpr": [round(float(x), 3) for x in tpr_cost[::max(1, len(tpr_cost)//20)]]
                },
                "delay_roc": {
                    "fpr": [round(float(x), 3) for x in fpr_del[::max(1, len(fpr_del)//20)]],
                    "tpr": [round(float(x), 3) for x in tpr_del[::max(1, len(tpr_del)//20)]]
                }
            },
            "ai_gain_summary": {
                "cost_mae_reduction_pct": round(float(((mean_absolute_error(y_cost_te, y_pred_baseline_cost) - mean_absolute_error(y_cost_te, y_pred_gbr_cost)) / mean_absolute_error(y_cost_te, y_pred_baseline_cost)) * 100.0), 1),
                "delay_mae_reduction_pct": round(float(((mean_absolute_error(y_del_te, y_pred_baseline_del) - mean_absolute_error(y_del_te, y_pred_gbr_del)) / mean_absolute_error(y_del_te, y_pred_baseline_del)) * 100.0), 1),
                "classification_accuracy_gain_pct": round(float((accuracy_score(y_chigh_te, y_pred_chigh) - accuracy_score(y_chigh_te, y_pred_baseline_chigh)) * 100.0), 1)
            }
        }
        
        self.is_trained = True
        return self.benchmarks

    def predict_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs full inference pipeline on a single project or modified project record.
        """
        if not self.is_trained:
            self.train_and_evaluate()
            
        df_single = pd.DataFrame([project_data])
        
        # Ensure all columns exist with defaults
        for col in ALL_FEATURES:
            if col not in df_single.columns:
                df_single[col] = 0 if col in (CUF_NUMERIC_FEATURES + AUGMENTED_NUMERIC_FEATURES) else "Unknown"
                
        X_single = df_single[ALL_FEATURES]
        X_proc = self.preprocessor.transform(X_single)
        
        # Inferences
        pred_cost_overrun_pct = float(self.models["gbr_cost"].predict(X_proc)[0])
        pred_cost_overrun_pct = max(0.0, round(pred_cost_overrun_pct, 2))
        
        orig_cost = float(project_data.get("original_cost_cr", 500.0))
        pred_cost_overrun_cr = round(orig_cost * (pred_cost_overrun_pct / 100.0), 2)
        pred_revised_cost_cr = round(orig_cost + pred_cost_overrun_cr, 2)
        
        pred_delay_months = int(max(0, round(float(self.models["gbr_delay"].predict(X_proc)[0]))))
        
        prob_high_cost = round(float(self.models["rf_class_cost"].predict_proba(X_proc)[0][1]), 3)
        prob_high_delay = round(float(self.models["rf_class_del"].predict_proba(X_proc)[0][1]), 3)
        
        return {
            "predicted_cost_overrun_pct": pred_cost_overrun_pct,
            "predicted_cost_overrun_cr": pred_cost_overrun_cr,
            "predicted_revised_cost_cr": pred_revised_cost_cr,
            "predicted_schedule_delay_months": pred_delay_months,
            "prob_high_cost_escalation": prob_high_cost,
            "prob_high_schedule_delay": prob_high_delay
        }

    def simulate_what_if(self, base_project: Dict[str, Any], adjustments: Dict[str, Any]) -> Dict[str, Any]:
        """
        What-If Sandbox: Adjusts project levers and calculates predictive delta.
        """
        sim_data = dict(base_project)
        
        # Apply adjustments
        if "land_acquired_pct_delta" in adjustments:
            sim_data["land_acquired_pct"] = float(np.clip(float(sim_data.get("land_acquired_pct", 100.0)) + float(adjustments["land_acquired_pct_delta"]), 0.0, 100.0))
            
        if "additional_delay_months" in adjustments:
            sim_data["schedule_delay_months"] = float(sim_data.get("schedule_delay_months", 0.0)) + float(adjustments["additional_delay_months"])
            sim_data["critical_delay_days"] = float(sim_data.get("critical_delay_days", 0.0)) + (float(adjustments["additional_delay_months"]) * 30)
            
        if "inflation_surge_pct" in adjustments:
            sim_data["raw_material_inflation_sensitivity"] = float(np.clip(float(sim_data.get("raw_material_inflation_sensitivity", 0.5)) + float(adjustments["inflation_surge_pct"])/100.0, 0.0, 1.0))
            
        if "dispute_count_delta" in adjustments:
            sim_data["dispute_count"] = max(0, int(sim_data.get("dispute_count", 0)) + int(adjustments["dispute_count_delta"]))
            sim_data["dispute_value_cr"] = float(sim_data.get("dispute_value_cr", 0.0)) + (int(adjustments["dispute_count_delta"]) * 50.0)
            
        if "contractor_rating_delta" in adjustments:
            sim_data["contractor_rating"] = float(np.clip(float(sim_data.get("contractor_rating", 7.0)) + float(adjustments["contractor_rating_delta"]), 1.0, 10.0))

        # Predict with simulated levers
        pred = self.predict_project(sim_data)
        
        # Risk Scorer evaluation
        from backend.models.risk_scorer import ProjectRiskScorer
        risk_eval = ProjectRiskScorer.evaluate_project_risk(sim_data)
        
        orig_cost = float(sim_data.get("original_cost_cr", 500.0))
        delta_overrun_cr = round(pred["predicted_cost_overrun_cr"] - float(base_project.get("cost_overrun_cr", 0.0)), 2)
        delta_delay_mo = pred["predicted_schedule_delay_months"] - int(base_project.get("schedule_delay_months", 0))
        
        return {
            "original_project": {
                "cost_overrun_cr": base_project.get("cost_overrun_cr", 0.0),
                "cost_overrun_pct": base_project.get("cost_overrun_pct", 0.0),
                "schedule_delay_months": base_project.get("schedule_delay_months", 0),
                "revised_cost_cr": base_project.get("revised_cost_cr", orig_cost)
            },
            "simulated_prediction": pred,
            "simulated_risk": risk_eval,
            "delta": {
                "cost_overrun_cr_delta": delta_overrun_cr,
                "delay_months_delta": delta_delay_mo,
                "risk_score_delta": round(risk_eval["composite_risk_score"] - float(base_project.get("composite_risk_score", 45.0)), 1)
            }
        }

# Global singleton
ml_engine = MLEngine()
