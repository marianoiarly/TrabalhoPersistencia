from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from app.database import getSession
from app.models import Laboratorio, Equipamento, Experimento
from app.schemas.entities import LaboratorioCreate, LaboratorioPublic, LaboratorioUpdate
from app.crud.laboratorios import consultar_laboratorios

router = APIRouter(prefix="/laboratorios", tags=["Laboratorios"])

@router.post("/", response_model=LaboratorioPublic, status_code=201)
def criar_laboratorio(dados: LaboratorioCreate, session: Session = Depends(getSession)):
    laboratorio = Laboratorio.model_validate(dados)
    session.add(laboratorio)
    session.commit()
    session.refresh(laboratorio)
    return laboratorio

@router.get("/", response_model=list[LaboratorioPublic])
def listar_laboratorios(nome: str | None = None, ativo: bool | None = None, session: Session = Depends(getSession)):
    return consultar_laboratorios(session, nome, ativo)

@router.get("/{laboratorio_id}", response_model=LaboratorioPublic)
def buscar_laboratorio(laboratorio_id: int, session: Session = Depends(getSession)):
    laboratorio = session.get(Laboratorio, laboratorio_id)
    if laboratorio is None:
        raise HTTPException(404, "Lab nao encontrado")
    return laboratorio

@router.patch("/{laboratorio_id}", response_model=LaboratorioPublic)
def atualizar_laboratorio(laboratorio_id: int, dados: LaboratorioUpdate, session: Session = Depends(getSession)):
    laboratorio = session.get(Laboratorio, laboratorio_id)
    if laboratorio is None:
        raise HTTPException(404, "Lab nao encontrado")
    valores = dados.model_dump(exclude_unset=True)
    if any(v is None for k, v in valores.items() if k in {"nome", "localizacao", "ativo"}):
        raise HTTPException(422, "obrigatorio nao pode ser nulo")
    laboratorio.sqlmodel_update(valores)
    session.add(laboratorio)
    session.commit()
    session.refresh(laboratorio)
    return laboratorio

@router.delete("/{laboratorio_id}", status_code=204)
def excluir_laboratorio(laboratorio_id: int, session: Session = Depends(getSession)):
    laboratorio = session.get(Laboratorio, laboratorio_id)
    if laboratorio is None:
        raise HTTPException(404, "Lab nao encontrado")
    if session.exec(select(Equipamento.id).where(Equipamento.laboratorio_id == laboratorio_id)).first() is not None:
        raise HTTPException(409, "Lab possui equipamentos")
    if session.exec(select(Experimento.id).where(Experimento.laboratorio_id == laboratorio_id)).first() is not None:
        raise HTTPException(409, "Lab possui experimentos")
    session.delete(laboratorio)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Nao e possivel excluir lab")
