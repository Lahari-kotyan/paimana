"""
Common Upload Form (CUF) Attribution & Feature Contribution Analysis Engine
Quantifies the predictive signal from native CUF fields vs newly augmented exogenous variables.
Directly addresses SIH Theme Dimension (c).
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error, accuracy_score
from backend.config import DATA_DIR
from backend.models.ml_engine import CUF_NUMERIC_FEATURES, AUGMENTED_NUMERIC_FEATURES

class CUFAttributionEngine:
    """
    Performs empirical comparative study and feature attribution between:
    1. Base CUF Fields (Cost, Milestones, Expenditure, Dates, Progress %)
    2. Augmented Exogenous Variables (Land Acquisition, Clearances, Contractor Rating, Disputes, Inflation)
    """
    
    @staticmethod
    def run_attribution_study() -> Dict[str, Any]:
        csv_path = DATA_DIR / "paimana_projects_1981.csv"
        df = pd.read_csv(csv_path)
        
        y_cost = df["cost_overrun_pct"].values
        y_delay = df["schedule_delay_months"].values
        y_high_cost = df["is_high_cost_overrun"].values
        
        # 1. Train CUF-Only Model
        X_cuf = df[CUF_NUMERIC_FEATURES]
        X_cuf_tr, X_cuf_te, y_c_tr, y_c_te, y_d_tr, y_d_te, y_hc_tr, y_hc_te = train_test_split(
            X_cuf, y_cost, y_delay, y_high_cost, test_size=0.20, random_state=42
        )
        
        rf_cuf_cost = RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42)
        rf_cuf_cost.fit(X_cuf_tr, y_c_tr)
        y_pred_cuf_cost = rf_cuf_cost.predict(X_cuf_te)
        
        r2_cuf_cost = round(float(r2_score(y_c_te, y_pred_cuf_cost)), 3)
        mae_cuf_cost = round(float(mean_absolute_error(y_c_te, y_pred_cuf_cost)), 2)
        
        # 2. Train Full Augmented Model (CUF + Augmented features)
        all_numeric = CUF_NUMERIC_FEATURES + AUGMENTED_NUMERIC_FEATURES
        X_all = df[all_numeric]
        X_all_tr, X_all_te, _, _, _, _, _, _ = train_test_split(
            X_all, y_cost, y_delay, y_high_cost, test_size=0.20, random_state=42
        )
        
        rf_all_cost = GradientBoostingRegressor(n_estimators=120, max_depth=5, learning_rate=0.08, random_state=42)
        rf_all_cost.fit(X_all_tr, y_c_tr)
        y_pred_all_cost = rf_all_cost.predict(X_all_te)
        
        r2_all_cost = round(float(r2_score(y_c_te, y_pred_all_cost)), 3)
        mae_all_cost = round(float(mean_absolute_error(y_c_te, y_pred_all_cost)), 2)
        
        # 3. Compute Feature Importances
        importances = rf_all_cost.feature_importances_
        feature_importance_list = []
        
        cuf_total_importance = 0.0
        aug_total_importance = 0.0
        
        for feat_name, imp in zip(all_numeric, importances):
            is_cuf = feat_name in CUF_NUMERIC_FEATURES
            pct = round(float(imp * 100.0), 2)
            if is_cuf:
                cuf_total_importance += imp
                source = "Native CUF Field"
            else:
                aug_total_importance += imp
                source = "Augmented Exogenous Indicator"
                
            feature_importance_list.append({
                "feature": feat_name,
                "importance_pct": pct,
                "source": source,
                "is_cuf": is_cuf
            })
            
        feature_importance_list = sorted(feature_importance_list, key=lambda x: x["importance_pct"], reverse=True)
        
        cuf_share_pct = round(float(cuf_total_importance / (cuf_total_importance + aug_total_importance) * 100.0), 1)
        aug_share_pct = round(float(aug_total_importance / (cuf_total_importance + aug_total_importance) * 100.0), 1)
        
        r2_gain_pct = round(float(((r2_all_cost - r2_cuf_cost) / max(0.01, r2_cuf_cost)) * 100.0), 1)
        mae_reduction_pct = round(float(((mae_cuf_cost - mae_all_cost) / mae_cuf_cost) * 100.0), 1)
        
        return {
            "cuf_only_model": {
                "features_used": len(CUF_NUMERIC_FEATURES),
                "r2_score": r2_cuf_cost,
                "mae": mae_cuf_cost,
                "description": "Prediction based solely on standard PAIMANA / OCMS Common Upload Form inputs."
            },
            "augmented_model": {
                "features_used": len(all_numeric),
                "r2_score": r2_all_cost,
                "mae": mae_all_cost,
                "description": "Prediction incorporating external land acquisition, vendor disputes, and inflation indicators."
            },
            "attribution_summary": {
                "cuf_signal_share_pct": cuf_share_pct,
                "augmented_signal_share_pct": aug_share_pct,
                "r2_improvement_pct": r2_gain_pct,
                "mae_error_reduction_pct": mae_reduction_pct,
                "key_finding": f"Existing CUF fields capture {cuf_share_pct}% of predictive signal, while newly augmented variables provide {aug_share_pct}% incremental signal, reducing prediction error by {mae_reduction_pct}%."
            },
            "feature_importance_rankings": feature_importance_list
        }
