import io, json, os
import pandas as pd
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from app.core.config import settings
from app.db.database import SessionLocal
from app.db.models import User, Dataset, Experiment, ModelRegistry
from app.auth.security import hash_password, verify_password, create_token
from app.auth.deps import current_user
from app.ml.runner import run
from app.services.mlflow_service import log_experiment

router = APIRouter(prefix="/api")

@router.get("/health")
def health():
    return {"status":"ok","version":"5.0.0","features":["auth","registry","shap","mlflow"]}

@router.post("/auth/register")
def register(username: str = Form(...), password: str = Form(...)):
    db=SessionLocal()
    if db.query(User).filter_by(username=username).first():
        db.close(); raise HTTPException(400,"Username already exists")
    u=User(username=username,password_hash=hash_password(password))
    db.add(u); db.commit(); db.close()
    return {"message":"registered"}

@router.post("/auth/login")
def login(username: str = Form(...), password: str = Form(...)):
    db=SessionLocal(); u=db.query(User).filter_by(username=username).first(); db.close()
    if not u or not verify_password(password,u.password_hash):
        raise HTTPException(401,"Invalid credentials")
    return {"access_token":create_token(username),"token_type":"bearer"}

@router.post("/experiment")
async def experiment(file: UploadFile=File(...), target: str=Form(...),
                     task: str=Form("classification"), model: str=Form("auto"),
                     name: str=Form("Experiment"), user=Depends(current_user)):
    try:
        df=pd.read_csv(io.BytesIO(await file.read()))
        result=run(df,target,task,model,settings.model_dir)
        db=SessionLocal()
        ds=Dataset(name=file.filename,rows=len(df),columns=len(df.columns),
                   schema_json=json.dumps({c:str(df[c].dtype) for c in df.columns}))
        db.add(ds); db.commit(); db.refresh(ds)
        row=Experiment(user_id=None,dataset_id=ds.id,name=name,task=task,target=target,
                       model=result["model"],metric=result["metric"],score=result["score"],
                       model_file=result["model_file"],metadata_json=json.dumps(result))
        db.add(row); db.commit(); db.refresh(row)
        reg=ModelRegistry(name=result["model"],version=1,experiment_id=row.id,
                          stage="candidate",artifact=result["model_file"])
        db.add(reg); db.commit()
        run_id=log_experiment(result,{"task":task,"target":target,"model":result["model"]})
        row.run_id=run_id; db.commit(); db.close()
        result["id"]=row.id; result["registry_stage"]="candidate"
        return result
    except Exception as e:
        raise HTTPException(400,str(e))

@router.get("/history")
def history(user=Depends(current_user)):
    db=SessionLocal()
    rows=db.query(Experiment).order_by(Experiment.id.desc()).all()
    out=[{"id":r.id,"name":r.name,"task":r.task,"target":r.target,"model":r.model,
          "metric":r.metric,"score":r.score,"created_at":r.created_at.isoformat()} for r in rows]
    db.close(); return out

@router.get("/registry")
def registry(user=Depends(current_user)):
    db=SessionLocal()
    rows=db.query(ModelRegistry).order_by(ModelRegistry.id.desc()).all()
    out=[{"id":r.id,"name":r.name,"version":r.version,"stage":r.stage,
          "experiment_id":r.experiment_id,"artifact":r.artifact} for r in rows]
    db.close(); return out

@router.get("/models/{filename}")
def download_model(filename:str, user=Depends(current_user)):
    path=os.path.join(settings.model_dir,os.path.basename(filename))
    if not os.path.exists(path): raise HTTPException(404,"Model not found")
    return FileResponse(path,filename=os.path.basename(path),media_type="application/octet-stream")
