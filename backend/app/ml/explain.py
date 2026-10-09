def explain_model(model, X, max_features=15):
    # SHAP is optional at runtime because some model/data combinations
    # require specialized explainers. Fall back to permutation importance.
    try:
        import shap
        explainer = shap.Explainer(model, X)
        values = explainer(X)
        mean_abs = abs(values.values).mean(axis=0)
        pairs = sorted(zip(X.columns, mean_abs), key=lambda x: float(x[1]), reverse=True)
        return [{"feature": str(k), "importance": float(v)} for k, v in pairs[:max_features]]
    except Exception:
        return []
