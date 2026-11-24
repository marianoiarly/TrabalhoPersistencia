from fastapi import FastAPI
from app.routers import laboratorios, usuarios, equipamentos, experimentos, manutencoes, reservas, relatorios

app = FastAPI()

@app.get("/")
def inicio():
    return {"mensagem": "Sistema de Gestao de Laboratorio"}

app.include_router(laboratorios.router)
app.include_router(usuarios.router)
app.include_router(equipamentos.router)
app.include_router(experimentos.router)
app.include_router(manutencoes.router)
app.include_router(reservas.router)
app.include_router(relatorios.router)
