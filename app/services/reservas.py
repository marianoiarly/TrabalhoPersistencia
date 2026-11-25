from datetime import datetime
from fastapi import HTTPException
from sqlmodel import Session, select
from app.models import (
    Equipamento,
    Usuario,
    Laboratorio,
    Experimento,
    Reserva,
    Manutencao,
)


def validar_reserva(
    session: Session,
    equipamento_id: int,
    usuario_id: int,
    experimento_id: int | None,
    inicio: datetime,
    fim: datetime,
    ignorar_id: int | None = None,
):
    if inicio >= fim:
        raise HTTPException(400, "A data final deve ser posterior a inicial")
    equipamento = session.exec(
        select(Equipamento).where(Equipamento.id == equipamento_id).with_for_update()
    ).first()
    if equipamento is None:
        raise HTTPException(404, "Equipamento nao encontrado")
    laboratorio = session.get(Laboratorio, equipamento.laboratorio_id)
    if (
        not equipamento.ativo
        or equipamento.status != "disponivel"
        or not laboratorio.ativo
    ):
        raise HTTPException(409, "Equipamento ou laboratorio indisponivel")
    usuario = session.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(404, "Usuario nao encontrado")
    if not usuario.ativo:
        raise HTTPException(409, "Usuario inativo")
    if experimento_id is not None:
        experimento = session.get(Experimento, experimento_id)
        if experimento is None:
            raise HTTPException(404, "Experimento nao encontrado")
        if experimento.laboratorio_id != equipamento.laboratorio_id:
            raise HTTPException(409, "Experimento pertence a outro laboratorio")
        if equipamento not in experimento.equipamentos:
            raise HTTPException(409, "Equipamento nao esta vinculado ao experimento")
    consulta = select(Reserva).where(
        Reserva.equipamento_id == equipamento_id,
        Reserva.status == "ativa",
        Reserva.inicio < fim,
        Reserva.fim > inicio,
    )
    if ignorar_id is not None:
        consulta = consulta.where(Reserva.id != ignorar_id)
    if session.exec(consulta).first() is not None:
        raise HTTPException(409, "Equipamento ja reservado neste periodo")
    manutencao = session.exec(
        select(Manutencao).where(
            Manutencao.equipamento_id == equipamento_id,
            Manutencao.status == "aberta",
            Manutencao.inicio < fim,
            (Manutencao.fim.is_(None) | (Manutencao.fim > inicio)),
        )
    ).first()
    if manutencao is not None:
        raise HTTPException(409, "Equipamento em manutencao neste periodo")


def verificar_disponibilidade(
    session: Session, equipamento_id: int, inicio: datetime, fim: datetime
):
    equipamento = session.get(Equipamento, equipamento_id)
    if equipamento is None:
        raise HTTPException(404, "Equipamento nao encontrado")
    if inicio >= fim:
        raise HTTPException(400, "Periodo invalido")
    laboratorio = session.get(Laboratorio, equipamento.laboratorio_id)
    if (
        not equipamento.ativo
        or equipamento.status != "disponivel"
        or not laboratorio.ativo
    ):
        return {"equipamento_id": equipamento_id, "disponivel": False}
    reserva = session.exec(
        select(Reserva).where(
            Reserva.equipamento_id == equipamento_id,
            Reserva.status == "ativa",
            Reserva.inicio < fim,
            Reserva.fim > inicio,
        )
    ).first()
    manutencao = session.exec(
        select(Manutencao).where(
            Manutencao.equipamento_id == equipamento_id,
            Manutencao.status == "aberta",
            Manutencao.inicio < fim,
            (Manutencao.fim.is_(None) | (Manutencao.fim > inicio)),
        )
    ).first()
    return {
        "equipamento_id": equipamento_id,
        "disponivel": reserva is None and manutencao is None,
    }
