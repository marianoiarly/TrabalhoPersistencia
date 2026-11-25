from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session
from app.database import getSession
from app.models import Reserva
from app.schemas.entities import ReservaCreate, ReservaPublic, ReservaUpdate
from app.crud.reservas import consultar_reservas
from app.services.reservas import validar_reserva, verificar_disponibilidade

router = APIRouter(prefix="/reservas", tags=["Reservas"])

@router.post("/", response_model=ReservaPublic, status_code=201)
def criar_reserva(dados: ReservaCreate, session: Session = Depends(getSession)):
    if dados.status != "ativa":
        raise HTTPException(400, "Nova reserva deve iniciar ativa")
    validar_reserva(session, dados.equipamento_id, dados.usuario_id, dados.experimento_id, dados.inicio, dados.fim)
    reserva = Reserva.model_validate(dados)
    session.add(reserva)
    try:
        session.commit()
        session.refresh(reserva)
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Nao foi possivel registrar a reserva")
    return reserva

@router.get("/", response_model=list[ReservaPublic])
def listar_reservas(equipamento_id: int | None = None, usuario_id: int | None = None,
                    status: str | None = None, inicio: datetime | None = None, fim: datetime | None = None,
                    session: Session = Depends(getSession)):
    return consultar_reservas(session, equipamento_id, usuario_id, status, inicio, fim)

@router.get("/disponibilidade")
def disponibilidade(equipamento_id: int, inicio: datetime, fim: datetime,
                     session: Session = Depends(getSession)):
    return verificar_disponibilidade(session, equipamento_id, inicio, fim)

@router.get("/{reserva_id}", response_model=ReservaPublic)
def buscar_reserva(reserva_id: int, session: Session = Depends(getSession)):
    reserva = session.get(Reserva, reserva_id)
    if reserva is None:
        raise HTTPException(404, "Reserva nao encontrada")
    return reserva

@router.patch("/{reserva_id}", response_model=ReservaPublic)
def atualizar_reserva(reserva_id: int, dados: ReservaUpdate, session: Session = Depends(getSession)):
    reserva = session.get(Reserva, reserva_id)
    if reserva is None:
        raise HTTPException(404, "Reserva nao encontrada")
    valores = dados.model_dump(exclude_unset=True)
    if any(v is None for k, v in valores.items() if k in {"equipamento_id", "usuario_id", "inicio", "fim", "status"}):
        raise HTTPException(422, "Campo obrigatorio nao pode ser nulo")
    status = valores.get("status", reserva.status)
    if status not in {"ativa", "cancelada", "concluida"}:
        raise HTTPException(400, "Status invalido")
    if reserva.status != "ativa" and status == "ativa":
        raise HTTPException(409, "Reserva encerrada nao pode ser reativada")
    if status == "ativa":
        validar_reserva(
            session,
            valores.get("equipamento_id", reserva.equipamento_id),
            valores.get("usuario_id", reserva.usuario_id),
            valores.get("experimento_id", reserva.experimento_id),
            valores.get("inicio", reserva.inicio),
            valores.get("fim", reserva.fim),
            ignorar_id=reserva.id
        )
    reserva.sqlmodel_update(valores)
    session.add(reserva)
    try:
        session.commit()
        session.refresh(reserva)
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Operacao viola restricoes do banco")
    return reserva

@router.delete("/{reserva_id}", status_code=204)
def excluir_reserva(reserva_id: int, session: Session = Depends(getSession)):
    reserva = session.get(Reserva, reserva_id)
    if reserva is None:
        raise HTTPException(404, "Reserva nao encontrada")
    session.delete(reserva)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Operacao viola restricoes do banco")
