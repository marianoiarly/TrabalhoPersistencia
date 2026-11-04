from fastapi import FastAPI
from app.database import create_db_and_tables

app = FastAPI()

@app.on_event("startup")
def startup():
    create_db_and_tables()

@app.get("/")
def inicio():
    return {"mensagem": "Sistema de Gestao de Laboratorio"}
