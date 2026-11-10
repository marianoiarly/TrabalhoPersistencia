import os
from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./laboratorio.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args=connect_args,
)

if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def habilitar_chaves_estrangeiras(conexao, registro):
        cursor = conexao.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

def create_db_and_tables():
    from app import models
    SQLModel.metadata.create_all(engine)

def getSession():
    with Session(engine) as session:
        yield session
