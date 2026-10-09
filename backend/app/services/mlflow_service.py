def log_experiment(result, params=None):
    try:
        import mlflow
        mlflow.log_params(params or {})
        mlflow.log_metric(result["metric"], result["score"])
        return mlflow.active_run().info.run_id if mlflow.active_run() else None
    except Exception:
        return None
