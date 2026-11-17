from fastapi import FastAPI
from .database import engine, Base
from . import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Interview Copilot")

@app.get("/health")
def health():
    return {"status": "ok"}