import models
from typing import Annotated, Union
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

origins = [
    'http://localhost:3000'
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TransactionBase(BaseModel):
    amount: float
    category: Union[str, None] = None
    description: Union[str, None] = None
    is_income: bool = False
    date: Union[str, None] = None  # Use str for simplicity, consider DateTime for real applications

class TransactionModel(TransactionBase):
    id: int

    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_depends = Annotated[Session, Depends(get_db)]

models.Base.metadata.create_all(bind=engine)

@app.post("/transactions/", response_model=TransactionModel)
async def create_transaction(
    transaction: TransactionBase,
    db: db_depends
):
    db_transaction = models.Transaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@app.get("/transactions/", response_model=list[TransactionModel])
async def read_transactions(
    db: db_depends,
    skip: int = 0,
    limit: int = 100
):
    transactions = db.query(models.Transaction).offset(skip).limit(limit).all()
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found")
    return transactions