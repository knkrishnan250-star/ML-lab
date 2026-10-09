from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "ML Experiment Lab"
    secret_key: str = "change-this-in-production"
    database_url: str = "sqlite:///./experiments.db"
    model_dir: str = "models"
    mlflow_tracking_uri: str = "sqlite:///./mlflow.db"

    class Config:
        env_file = ".env"

settings = Settings()
