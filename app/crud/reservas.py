from datetime import datetime
from sqlmodel import Session, select
from app.models import Reserva


def consultar_reservas(
    session: Session,
    equipamento_id: int | None = None,
    usuario_id: int | None = None,
    status: str | None = None,
    inicio: datetime | None = None,
    fim: datetime | None = None,
):
    consulta = select(Reserva)
    if equipamento_id is not None:
        consulta = consulta.where(Reserva.equipamento_id == equipamento_id)
    if usuario_id is not None:
        consulta = consulta.where(Reserva.usuario_id == usuario_id)
    if status:
        consulta = consulta.where(Reserva.status == status)
    if inicio is not None:
        consulta = consulta.where(Reserva.fim > inicio)
    if fim is not None:
        consulta = consulta.where(Reserva.inicio < fim)
    return session.exec(consulta.order_by(Reserva.inicio)).all()
