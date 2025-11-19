# pylint: disable=E0611
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datatbase import Base, engine, SessionLocal
from sqlalchemy import Column, Integer, String

app = FastAPI()

# SQLAlchemy Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True, unique=True)

Base.metadata.create_all(bind=engine)

# Pydantic Schemas
class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True  # FIXED

# DB Session Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create user route
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/",response_model=List[UserResponse])
def get_users(db:Session=Depends(get_db)):
    return db.query(User).all()

@app.get("/users/{user_id}",response_model=UserResponse)
def get_user(user_id:int,db:Session=Depends(get_db)):
    user=db.query(User).filter(User.id==user_id).first()
    if not user:
        raise HTTPException(404,"user not found")
    else:
        return user

@app.put("/users/{user_id}",response_model=UserResponse)
def update_user(user_id: int, updated_data: UserCreate, db: Session = Depends(get_db)):

    user=db.query(User).filter(User.id==user_id).first()
    if not user:
        raise HTTPException(404,"user not found")
    user.name=updated_data.name
    user.email=updated_data.email
    db.commit()
    db.refresh(user)
    return user

@app.delete("/users/{user_id}")
def delete_user(user_id:int,db:Session=Depends(get_db)):
    user=db.query(User).filter(User.id==user_id).first()
    if not user:
        raise HTTPException(404,"user not found")
    db.delete(user)
    db.commit()
    return {"message":"user deleted successfully"}