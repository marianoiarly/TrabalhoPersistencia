from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import getSession
from app.models import Experimento, Reserva
from app.schemas.entities import ExperimentoCreate, ExperimentoPublic, ExperimentoUpdate
from app.services.experimentos import validar_experimento

router = APIRouter(prefix="/experimentos", tags=["Experimentos"])

@router.post("/", response_model=ExperimentoPublic, status_code=201)
def criar_experimento(dados: ExperimentoCreate, session: Session = Depends(getSession)):
    equipamentos = validar_experimento(session, dados.laboratorio_id, dados.responsavel_id, dados.equipamento_ids)
    experimento = Experimento.model_validate(dados.model_dump(exclude={"equipamento_ids"}))
    experimento.equipamentos = equipamentos
    session.add(experimento)
    session.commit()
    session.refresh(experimento)
    return experimento

@router.get("/", response_model=list[ExperimentoPublic])
def listar_experimentos(laboratorio_id: int | None = None, responsavel_id: int | None = None,
                        session: Session = Depends(getSession)):
    consulta = select(Experimento)
    if laboratorio_id is not None:
        consulta = consulta.where(Experimento.laboratorio_id == laboratorio_id)
    if responsavel_id is not None:
        consulta = consulta.where(Experimento.responsavel_id == responsavel_id)
    return session.exec(consulta.order_by(Experimento.nome)).all()

@router.get("/{experimento_id}", response_model=ExperimentoPublic)
def buscar_experimento(experimento_id: int, session: Session = Depends(getSession)):
    experimento = session.get(Experimento, experimento_id)
    if experimento is None:
        raise HTTPException(404, "Experimento nao encontrado")
    return experimento

@router.patch("/{experimento_id}", response_model=ExperimentoPublic)
def atualizar_experimento(experimento_id: int, dados: ExperimentoUpdate, session: Session = Depends(getSession)):
    experimento = session.get(Experimento, experimento_id)
    if experimento is None:
        raise HTTPException(404, "Experimento nao encontrado")
    valores = dados.model_dump(exclude_unset=True)
    ids = valores.pop("equipamento_ids", None)
    if any(v is None for k, v in valores.items() if k in {"nome", "laboratorio_id", "responsavel_id"}):
        raise HTTPException(422, "Campos obrigatorios nao podem ser nulos")
    laboratorio_id = valores.get("laboratorio_id", experimento.laboratorio_id)
    responsavel_id = valores.get("responsavel_id", experimento.responsavel_id)
    if ids is None:
        ids = [equipamento.id for equipamento in experimento.equipamentos]
    equipamentos = validar_experimento(session, laboratorio_id, responsavel_id, ids)
    experimento.sqlmodel_update(valores)
    experimento.equipamentos = equipamentos
    session.add(experimento)
    session.commit()
    session.refresh(experimento)
    return experimento

@router.delete("/{experimento_id}", status_code=204)
def excluir_experimento(experimento_id: int, session: Session = Depends(getSession)):
    experimento = session.get(Experimento, experimento_id)
    if experimento is None:
        raise HTTPException(404, "Experimento nao encontrado")
    if session.exec(select(Reserva.id).where(Reserva.experimento_id == experimento_id)).first() is not None:
        raise HTTPException(409, "Experimento possui reservas")
    experimento.equipamentos.clear()
    session.delete(experimento)
    session.commit()
