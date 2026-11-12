from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import getSession
from app.models import Manutencao, Equipamento, Reserva
from app.schemas.entities import ManutencaoCreate, ManutencaoPublic, ManutencaoUpdate

router = APIRouter(prefix="/manutencoes", tags=["Manutencoes"])

def validar_periodo(inicio: datetime, fim: datetime | None):
    if fim is not None and inicio >= fim:
        raise HTTPException(400, "Fim da manutencao deve ser posterior ao inicio")

@router.post("/", response_model=ManutencaoPublic, status_code=201)
def criar_manutencao(dados: ManutencaoCreate, session: Session = Depends(getSession)):
    if session.get(Equipamento, dados.equipamento_id) is None:
        raise HTTPException(404, "Equipamento nao encontrado")
    validar_periodo(dados.inicio, dados.fim)
    if dados.status not in {"aberta", "concluida"}:
        raise HTTPException(400, "Status de manutencao invalido")
    if dados.status == "aberta":
        conflito = session.exec(select(Reserva).where(
            Reserva.equipamento_id == dados.equipamento_id,
            Reserva.status == "ativa",
            Reserva.inicio < (dados.fim or datetime.max),
            Reserva.fim > dados.inicio
        )).first()
        if conflito is not None:
            raise HTTPException(409, "Equipamento possui reserva neste periodo")
    manutencao = Manutencao.model_validate(dados)
    session.add(manutencao)
    session.commit()
    session.refresh(manutencao)
    return manutencao

@router.get("/", response_model=list[ManutencaoPublic])
def listar_manutencoes(equipamento_id: int | None = None, status: str | None = None,
                       session: Session = Depends(getSession)):
    consulta = select(Manutencao)
    if equipamento_id is not None:
        consulta = consulta.where(Manutencao.equipamento_id == equipamento_id)
    if status:
        consulta = consulta.where(Manutencao.status == status)
    return session.exec(consulta.order_by(Manutencao.inicio.desc())).all()

@router.get("/{manutencao_id}", response_model=ManutencaoPublic)
def buscar_manutencao(manutencao_id: int, session: Session = Depends(getSession)):
    manutencao = session.get(Manutencao, manutencao_id)
    if manutencao is None:
        raise HTTPException(404, "Manutencao nao encontrada")
    return manutencao

@router.patch("/{manutencao_id}", response_model=ManutencaoPublic)
def atualizar_manutencao(manutencao_id: int, dados: ManutencaoUpdate, session: Session = Depends(getSession)):
    manutencao = session.get(Manutencao, manutencao_id)
    if manutencao is None:
        raise HTTPException(404, "Manutencao nao encontrada")
    valores = dados.model_dump(exclude_unset=True)
    if "equipamento_id" in valores:
        raise HTTPException(400, "Nao e permitido trocar o equipamento")
    status = valores.get("status", manutencao.status)
    if status not in {"aberta", "concluida"}:
        raise HTTPException(400, "Status de manutencao invalido")
    inicio = valores.get("inicio", manutencao.inicio)
    fim = valores.get("fim", manutencao.fim)
    validar_periodo(inicio, fim)
    if status == "aberta":
        conflito = session.exec(select(Reserva).where(
            Reserva.equipamento_id == manutencao.equipamento_id,
            Reserva.status == "ativa",
            Reserva.inicio < (fim or datetime.max),
            Reserva.fim > inicio
        )).first()
        if conflito is not None:
            raise HTTPException(409, "Equipamento possui reserva neste periodo")
    if any(v is None for k, v in valores.items() if k in {"descricao", "inicio", "status"}):
        raise HTTPException(422, "Campos obrigatorios nao podem ser nulos")
    manutencao.sqlmodel_update(valores)
    session.add(manutencao)
    session.commit()
    session.refresh(manutencao)
    return manutencao

@router.delete("/{manutencao_id}", status_code=204)
def excluir_manutencao(manutencao_id: int, session: Session = Depends(getSession)):
    manutencao = session.get(Manutencao, manutencao_id)
    if manutencao is None:
        raise HTTPException(404, "Manutencao nao encontrada")
    session.delete(manutencao)
    session.commit()
