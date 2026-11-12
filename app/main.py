from fastapi import FastAPI
from app.routers import laboratorios, usuarios, equipamentos, experimentos, manutencoes
from app.database import create_db_and_tables

app = FastAPI()


@app.on_event("startup")
def startup():
    create_db_and_tables()


@app.get("/")
def inicio():
    return {"mensagem": "Sistema de Gestao de Laboratorio"}


app.include_router(laboratorios.router)
app.include_router(usuarios.router)
app.include_router(equipamentos.router)
app.include_router(experimentos.router)
app.include_router(manutencoes.router)
