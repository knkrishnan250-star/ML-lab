from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
from app.db.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)

class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    version = Column(Integer, default=1)
    rows = Column(Integer)
    columns = Column(Integer)
    schema_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)

class Experiment(Base):
    __tablename__ = "experiments"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)
    dataset_id = Column(Integer, nullable=True)
    name = Column(String, default="Experiment")
    task = Column(String)
    target = Column(String)
    model = Column(String)
    metric = Column(String)
    score = Column(Float)
    model_file = Column(String, nullable=True)
    run_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(Text, default="{}")

class ModelRegistry(Base):
    __tablename__ = "model_registry"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    version = Column(Integer, default=1)
    experiment_id = Column(Integer)
    stage = Column(String, default="candidate")
    artifact = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
