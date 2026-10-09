from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import Base, engine
from app.api.routes import router

Base.metadata.create_all(bind=engine)
app=FastAPI(title=settings.app_name,version="5.0.0")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,
                   allow_methods=["*"],allow_headers=["*"])
app.include_router(router)

@app.get("/")
def root():
    return {"name":settings.app_name,"version":"5.0.0","docs":"/docs"}
