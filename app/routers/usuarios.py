from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from app.database import getSession
from app.models import Usuario, Reserva, Experimento
from app.schemas.entities import UsuarioCreate, UsuarioPublic, UsuarioUpdate
from app.crud.usuarios import consultar_usuarios

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/", response_model=UsuarioPublic, status_code=201)
def criar_usuario(dados: UsuarioCreate, session: Session = Depends(getSession)):
    usuario = Usuario.model_validate(dados)
    session.add(usuario)
    try:
        session.commit()
        session.refresh(usuario)
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Email ja cadastrado")
    return usuario

@router.get("/", response_model=list[UsuarioPublic])
def listar_usuarios(nome: str | None = None, ativo: bool | None = None, session: Session = Depends(getSession)):
    return consultar_usuarios(session, nome, ativo)

@router.get("/{usuario_id}", response_model=UsuarioPublic)
def buscar_usuario(usuario_id: int, session: Session = Depends(getSession)):
    usuario = session.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(404, "Usuario nao encontrado")
    return usuario

@router.patch("/{usuario_id}", response_model=UsuarioPublic)
def atualizar_usuario(usuario_id: int, dados: UsuarioUpdate, session: Session = Depends(getSession)):
    usuario = session.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(404, "Usuario nao encontrado")
    valores = dados.model_dump(exclude_unset=True)
    if any(v is None for v in valores.values()):
        raise HTTPException(422, "Campos nao podem ser nulos")
    usuario.sqlmodel_update(valores)
    session.add(usuario)
    try:
        session.commit()
        session.refresh(usuario)
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Email ja cadastrado")
    return usuario

@router.delete("/{usuario_id}", status_code=204)
def excluir_usuario(usuario_id: int, session: Session = Depends(getSession)):
    usuario = session.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(404, "Usuario nao encontrado")
    if session.exec(select(Reserva.id).where(Reserva.usuario_id == usuario_id)).first() is not None:
        raise HTTPException(409, "Usuario possui reservas")
    if session.exec(select(Experimento.id).where(Experimento.responsavel_id == usuario_id)).first() is not None:
        raise HTTPException(409, "Usuario e responsavel por experimentos")
    session.delete(usuario)
    session.commit()
