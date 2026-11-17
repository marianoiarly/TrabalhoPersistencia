from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlmodel import Session, select
from app.database import getSession
from app.models import Laboratorio, Equipamento, Usuario, Reserva, Manutencao, Experimento

router = APIRouter(prefix="/relatorios", tags=["Relatorios"])

@router.get("/usuarios/{usuario_id}/reservas")
def reservas_por_usuario(usuario_id: int, session: Session = Depends(getSession)):
    usuario = session.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(404, "Usuario nao encontrado")
    return usuario.reservas

@router.get("/equipamentos/{equipamento_id}/manutencoes")
def historico_manutencoes(equipamento_id: int, session: Session = Depends(getSession)):
    equipamento = session.get(Equipamento, equipamento_id)
    if equipamento is None:
        raise HTTPException(404, "Equipamento nao encontrado")
    return equipamento.manutencoes

@router.get("/experimentos/{experimento_id}/equipamentos")
def equipamentos_do_experimento(experimento_id: int, session: Session = Depends(getSession)):
    experimento = session.get(Experimento, experimento_id)
    if experimento is None:
        raise HTTPException(404, "Experimento nao encontrado")
    return experimento.equipamentos

@router.get("/reservas-detalhadas")
def reservas_detalhadas(inicio: datetime | None = None, fim: datetime | None = None,
                       status: str | None = None, session: Session = Depends(getSession)):
    consulta = (
        select(Reserva.id, Reserva.inicio, Reserva.fim, Reserva.status,
               Usuario.nome.label("usuario"), Equipamento.nome.label("equipamento"),
               Laboratorio.nome.label("laboratorio"))
        .join(Usuario, Usuario.id == Reserva.usuario_id)
        .join(Equipamento, Equipamento.id == Reserva.equipamento_id)
        .join(Laboratorio, Laboratorio.id == Equipamento.laboratorio_id)
    )
    if inicio is not None:
        consulta = consulta.where(Reserva.fim > inicio)
    if fim is not None:
        consulta = consulta.where(Reserva.inicio < fim)
    if status is not None:
        consulta = consulta.where(Reserva.status == status)
    registros = session.exec(consulta.order_by(Reserva.inicio)).all()
    return [
        {"id": r.id, "inicio": r.inicio, "fim": r.fim, "status": r.status,
         "usuario": r.usuario, "equipamento": r.equipamento, "laboratorio": r.laboratorio}
        for r in registros
    ]

@router.get("/equipamentos-disponiveis")
def equipamentos_disponiveis(inicio: datetime, fim: datetime, laboratorio_id: int | None = None,
                             session: Session = Depends(getSession)):
    if inicio >= fim:
        raise HTTPException(400, "Periodo invalido")
    reservas_ativas = select(Reserva.id).where(
        Reserva.equipamento_id == Equipamento.id,
        Reserva.status == "ativa",
        Reserva.inicio < fim,
        Reserva.fim > inicio
    ).correlate(Equipamento).exists()
    manutencoes_ativas = select(Manutencao.id).where(
        Manutencao.equipamento_id == Equipamento.id,
        Manutencao.status == "aberta",
        Manutencao.inicio < fim,
        (Manutencao.fim.is_(None) | (Manutencao.fim > inicio))
    ).correlate(Equipamento).exists()
    consulta = (
        select(Equipamento).join(Laboratorio, Laboratorio.id == Equipamento.laboratorio_id)
        .where(Equipamento.ativo == True, Equipamento.status == "disponivel", Laboratorio.ativo == True)
        .where(~reservas_ativas, ~manutencoes_ativas)
    )
    if laboratorio_id is not None:
        consulta = consulta.where(Equipamento.laboratorio_id == laboratorio_id)
    return session.exec(consulta.order_by(Equipamento.nome)).all()

@router.get("/estatisticas/reservas-por-equipamento")
def reservas_por_equipamento(session: Session = Depends(getSession)):
    consulta = (
        select(Equipamento.id, Equipamento.nome, func.count(Reserva.id).label("quantidade"))
        .outerjoin(Reserva, Reserva.equipamento_id == Equipamento.id)
        .group_by(Equipamento.id, Equipamento.nome)
        .order_by(func.count(Reserva.id).desc())
    )
    return [
        {"equipamento_id": row.id, "equipamento": row.nome, "quantidade_reservas": row.quantidade}
        for row in session.exec(consulta).all()
    ]

@router.get("/estatisticas/equipamentos-por-laboratorio")
def equipamentos_por_laboratorio(session: Session = Depends(getSession)):
    consulta = (
        select(Laboratorio.id, Laboratorio.nome, func.count(Equipamento.id).label("quantidade"))
        .outerjoin(Equipamento, Equipamento.laboratorio_id == Laboratorio.id)
        .group_by(Laboratorio.id, Laboratorio.nome)
    )
    return [
        {"laboratorio_id": row.id, "laboratorio": row.nome, "quantidade_equipamentos": row.quantidade}
        for row in session.exec(consulta).all()
    ]
