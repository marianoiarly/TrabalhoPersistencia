from sqlmodel import Session, select
from app.models import Laboratorio

def consultar_laboratorios(session: Session, nome: str | None = None, ativo: bool | None = None):
    consulta = select(Laboratorio)
    if nome:
        consulta = consulta.where(Laboratorio.nome.ilike(f"%{nome}%"))
    if ativo is not None:
        consulta = consulta.where(Laboratorio.ativo == ativo)
    return session.exec(consulta.order_by(Laboratorio.nome)).all()
