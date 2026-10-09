import os
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import f1_score, mean_squared_error
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.svm import SVC, SVR
from sklearn.neighbors import KNeighborsClassifier
from app.ml.explain import explain_model

try:
    from xgboost import XGBClassifier, XGBRegressor
except Exception:
    XGBClassifier = XGBRegressor = None

def models(task):
    if task == "classification":
        out = {
            "logistic_regression": Pipeline([("scale", StandardScaler()), ("model", LogisticRegression(max_iter=2000))]),
            "decision_tree": DecisionTreeClassifier(random_state=42),
            "random_forest": RandomForestClassifier(n_estimators=150, random_state=42),
            "svm": Pipeline([("scale", StandardScaler()), ("model", SVC(probability=True, random_state=42))]),
            "knn": Pipeline([("scale", StandardScaler()), ("model", KNeighborsClassifier())]),
        }
        if XGBClassifier:
            out["xgboost"] = XGBClassifier(n_estimators=120, max_depth=4, learning_rate=.08,
                subsample=.9, colsample_bytree=.9, eval_metric="logloss", random_state=42)
        return out
    out = {
        "ridge": Pipeline([("scale", StandardScaler()), ("model", Ridge())]),
        "decision_tree": DecisionTreeRegressor(random_state=42),
        "random_forest": RandomForestRegressor(n_estimators=150, random_state=42),
        "gradient_boosting": GradientBoostingRegressor(random_state=42),
        "svr": Pipeline([("scale", StandardScaler()), ("model", SVR())]),
    }
    if XGBRegressor:
        out["xgboost"] = XGBRegressor(n_estimators=150, max_depth=4, learning_rate=.08,
            subsample=.9, colsample_bytree=.9, objective="reg:squarederror", random_state=42)
    return out

def run(df, target, task, model_name="auto", model_dir="models"):
    if target not in df.columns:
        raise ValueError(f"Target '{target}' not found")
    data = df.dropna().copy()
    X = pd.get_dummies(data.drop(columns=[target]), drop_first=True)
    y = data[target]
    X = X.replace([np.inf, -np.inf], np.nan).dropna()
    y = y.loc[X.index]

    if task == "classification":
        if y.nunique() < 2:
            raise ValueError("Classification requires at least two classes")
        if y.dtype == "object":
            y = y.astype("category").cat.codes
    else:
        y = pd.to_numeric(y, errors="coerce")
        keep = y.notna()
        X, y = X.loc[keep], y.loc[keep]

    if len(X) < 10:
        raise ValueError("Use at least 10 valid rows for an experiment")

    stratify = y if task == "classification" and y.value_counts().min() >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=.2, random_state=42, stratify=stratify
    )

    registry = models(task)
    if model_name == "auto":
        scoring = "f1_weighted" if task == "classification" else "neg_root_mean_squared_error"
        scores = []
        for name, mdl in registry.items():
            try:
                s = cross_val_score(mdl, X_train, y_train, cv=3, scoring=scoring).mean()
                scores.append((name, float(s)))
            except Exception:
                pass
        if not scores:
            raise ValueError("No compatible model could train")
        model_name = max(scores, key=lambda x: x[1])[0]

    model = registry[model_name]
    model.fit(X_train, y_train)
    pred = model.predict(X_test)

    if task == "classification":
        score = float(f1_score(y_test, pred, average="weighted"))
        metric = "f1_weighted"
    else:
        score = float(mean_squared_error(y_test, pred) ** .5)
        metric = "rmse"

    perm = permutation_importance(model, X_test, y_test, n_repeats=5, random_state=42)
    order = np.argsort(perm.importances_mean)[::-1][:15]
    importance = [{"feature": str(X.columns[i]), "importance": float(perm.importances_mean[i])} for i in order]

    Path(model_dir).mkdir(parents=True, exist_ok=True)
    filename = f"{model_name}_{pd.Timestamp.utcnow().strftime('%Y%m%d%H%M%S%f')}.joblib"
    joblib.dump({"model": model, "features": list(X.columns), "task": task}, Path(model_dir)/filename)

    shap_values = explain_model(model, X_test)
    return {
        "model": model_name, "metric": metric, "score": score,
        "rows": int(len(data)), "columns": int(len(df.columns)),
        "features": list(X.columns), "importance": importance,
        "shap": shap_values, "model_file": filename
    }
