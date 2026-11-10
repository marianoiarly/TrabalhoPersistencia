from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from app.database import getSession
from app.models import Equipamento, Laboratorio, FichaTecnica, Reserva, Manutencao, ExperimentoEquipamento
from app.schemas.entities import (
    EquipamentoCreate, EquipamentoPublic, EquipamentoUpdate,
    FichaTecnicaCreate, FichaTecnicaPublic, FichaTecnicaUpdate
)
from app.crud.equipamentos import consultar_equipamentos
router = APIRouter(prefix="/equipamentos", tags=["Equipamentos"])
@router.post("/", response_model=EquipamentoPublic, status_code=201)
def criar_equipamento(dados: EquipamentoCreate, session: Session = Depends(getSession)):
    laboratorio = session.get(Laboratorio, dados.laboratorio_id)
    if laboratorio is None:
        raise HTTPException(404, "Laboratorio nao encontrado")
    if not laboratorio.ativo:
        raise HTTPException(409, "Laboratorio inativo")
    if dados.status not in {"disponivel", "indisponivel"}:
        raise HTTPException(400, "Status de equipamento invalido")
    equipamento = Equipamento.model_validate(dados)
    session.add(equipamento)
    try:

        session.commit()
        session.refresh(equipamento)
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Patrimonio ja cadastrado")
    return equipamento




@router.get("/")
def listar_equipamentos(pagina: int = Query(1, ge=1), tamanho_pagina: int = Query(10, ge=1, le=100),
                       nome: str | None = None, laboratorio_id: int | None = None, status: str | None = None,
                       session: Session = Depends(getSession)):
    return consultar_equipamentos(session, pagina, tamanho_pagina, nome, laboratorio_id, status)

@router.get("/{equipamento_id}", response_model=EquipamentoPublic)
def buscar_equipamento(equipamento_id: int, session: Session = Depends(getSession)):
    equipamento = session.get(Equipamento, equipamento_id)
    if equipamento is None:

        raise HTTPException(404, "Equipamento nao encontrado")
    return equipamento

@router.patch("/{equipamento_id}", response_model=EquipamentoPublic)

def atualizar_equipamento(equipamento_id: int, dados: EquipamentoUpdate, session: Session = Depends(getSession)):
    equipamento = session.get(Equipamento, equipamento_id)
    if equipamento is None:
        raise HTTPException(404, "Equipamento nao encontrado")
    valores = dados.model_dump(exclude_unset=True)
    if any(v is None for v in valores.values()):
        raise HTTPException(422, "Campos nao podem ser nulos")
    if "laboratorio_id" in valores and session.get(Laboratorio, valores["laboratorio_id"]) is None:
        raise HTTPException(404, "Laboratorio nao encontrado")
    if "status" in valores and valores["status"] not in {"disponivel", "indisponivel"}:
        raise HTTPException(400, "Status de equipamento invalido")
    equipamento.sqlmodel_update(valores)
    session.add(equipamento)
    try:
        session.commit()
        session.refresh(equipamento)
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Patrimonio ja cadastrado ou referencia invalida")
    return equipamento

@router.delete("/{equipamento_id}", status_code=204)

def excluir_equipamento(equipamento_id: int, session: Session = Depends(getSession)):
    equipamento = session.get(Equipamento, equipamento_id)
    if equipamento is None:
        raise HTTPException(404, "Equipamento nao encontrado")
    dependencias = [
        select(FichaTecnica.id).where(FichaTecnica.equipamento_id == equipamento_id),
        select(Reserva.id).where(Reserva.equipamento_id == equipamento_id),
        select(Manutencao.id).where(Manutencao.equipamento_id == equipamento_id),
        select(ExperimentoEquipamento.equipamento_id).where(ExperimentoEquipamento.equipamento_id == equipamento_id)
    ]
    if any(session.exec(consulta).first() is not None for consulta in dependencias):
        raise HTTPException(409, "Equipamento possui registros associados")
    session.delete(equipamento)
    session.commit()

@router.post("/fichas-tecnicas/", response_model=FichaTecnicaPublic, status_code=201)
def criar_ficha(dados: FichaTecnicaCreate, session: Session = Depends(getSession)):
    if session.get(Equipamento, dados.equipamento_id) is None:
        raise HTTPException(404, "Equipamento nao encontrado")
    ficha = FichaTecnica.model_validate(dados)
    session.add(ficha)
    try:
        session.commit()
        session.refresh(ficha)
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Equipamento ja possui ficha tecnica")
    return ficha
@router.get("/fichas-tecnicas/{ficha_id}", response_model=FichaTecnicaPublic)
def buscar_ficha(ficha_id: int, session: Session = Depends(getSession)):
    ficha = session.get(FichaTecnica, ficha_id)
    if ficha is None:
        raise HTTPException(404, "Ficha tecnica nao encontrada")
    return ficha

@router.patch("/fichas-tecnicas/{ficha_id}", response_model=FichaTecnicaPublic)
def atualizar_ficha(ficha_id: int, dados: FichaTecnicaUpdate, session: Session = Depends(getSession)):
    ficha = session.get(FichaTecnica, ficha_id)
    if ficha is None:
        raise HTTPException(404, "Ficha tecnica nao encontrada")
    valores = dados.model_dump(exclude_unset=True)
    if any(v is None for k, v in valores.items() if k in {"fabricante", "modelo"}):
        raise HTTPException(422, "Campos obrigatorios nao podem ser nulos")
    ficha.sqlmodel_update(valores)
    session.add(ficha)
    session.commit()
    session.refresh(ficha)
    return ficha

@router.delete("/fichas-tecnicas/{ficha_id}", status_code=204)
def excluir_ficha(ficha_id: int, session: Session = Depends(getSession)):
    ficha = session.get(FichaTecnica, ficha_id)
    if ficha is None:
        raise HTTPException(404, "Ficha tecnica nao encontrada")
    session.delete(ficha)
    session.commit()
