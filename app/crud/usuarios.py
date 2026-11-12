from sqlmodel import Session, select
from app.models import Usuario


def consultar_usuarios(
    session: Session, nome: str | None = None, ativo: bool | None = None
):
    consulta = select(Usuario)
    if nome:
        consulta = consulta.where(Usuario.nome.ilike(f"%{nome}%"))
    if ativo is not None:
        consulta = consulta.where(Usuario.ativo == ativo)
    return session.exec(consulta.order_by(Usuario.nome)).all()
