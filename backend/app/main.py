from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from . import models, schemas
from .security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Interview Copilot")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/register", response_model=schemas.UserOut, status_code=201)
def register(data: schemas.UserCreate, db: Session = Depends(get_db)):
    email = data.email.lower()

    existing = db.query(models.User).filter(models.User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = models.User(email=email, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/login", response_model=schemas.Token)
def login(data: schemas.UserLogin, db: Session = Depends(get_db)):
    email = data.email.lower()

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"access_token": create_access_token(user.id), "token_type": "bearer"}


bearer_scheme = HTTPBearer()


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    user_id = decode_access_token(creds.credentials)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.get(models.User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@app.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user