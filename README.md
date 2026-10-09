# ML Experiment Lab V5

A portfolio-focused ML experimentation platform with **FastAPI, React, SQLAlchemy, JWT authentication, XGBoost, SHAP, model registry and MLflow hooks**.

## V5 highlights

- User registration/login with JWT
- Persistent datasets and experiment history
- Automatic model selection
- Classification + regression
- XGBoost adapters
- SHAP explainability with graceful fallback
- Permutation feature importance
- Model artifact storage
- Candidate model registry
- MLflow metric/parameter logging hook
- Docker Compose
- GitHub Actions CI
- React dashboard

## Architecture

```text
React
  |
FastAPI + JWT
  |
  +-- Experiment Service
  |      +-- sklearn
  |      +-- XGBoost
  |      +-- SHAP
  |
  +-- SQLAlchemy
  |      +-- Users
  |      +-- Datasets
  |      +-- Experiments
  |      +-- Registry
  |
  +-- MLflow tracking
  |
  +-- Joblib model artifacts
```

## Run

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open the frontend URL and create an account.

API docs: `http://127.0.0.1:8000/docs`

## Docker

```bash
docker compose up --build
```

## Portfolio value

This version demonstrates ML engineering concepts beyond simply training a model: authentication, experiment persistence, model lifecycle, explainability, artifact management, API design, containerization and CI.

## Production hardening still required

Replace the development secret, restrict CORS, use HTTPS, move to PostgreSQL, add proper user ownership checks, secure model downloads, add rate limiting, validation and monitoring before deploying publicly.
