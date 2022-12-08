from fastapi import FastAPI, Depends
from sqlalchemy import MetaData
from sqlalchemy.orm import Session


import db_models
from db_connect import *



app = FastAPI()

meta = MetaData()

db_models.Base.metadata.create_all(bind=engine)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/create_problem")
async def create_problem(name: str,problem: str,date: float,no: int,type: str, db: Session = Depends(get_db)):
    new_problem = db_models.Problem(
        name = name,
        problem = problem,
        date = date,
        no = no,
        responsible = responsible
    )
    db.add(new_problem)
    db.commit()
    db.refresh
    return 

@app.post("/Create_new_user")
async def create_new_user(name: str,surname: str,responsible_for: str,tg: str, db: Session = Depends(get_db)):
    new_user = db_models.responsible(
        name = name,
        surname = surname,
        responsible_for = responsible_for,
        tg = tg
    )
    db.add(new_user)
    db.commit()
    return