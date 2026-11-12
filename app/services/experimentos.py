from fastapi import HTTPException
from sqlmodel import Session
from app.models import Equipamento, Laboratorio, Usuario

def validar_experimento(session: Session, laboratorio_id: int, responsavel_id: int, equipamento_ids: list[int]):
    laboratorio = session.get(Laboratorio, laboratorio_id)
    if laboratorio is None:
        raise HTTPException(404, "Laboratorio nao encontrado")
    if not laboratorio.ativo:
        raise HTTPException(409, "Laboratorio inativo")
    usuario = session.get(Usuario, responsavel_id)
    if usuario is None:
        raise HTTPException(404, "Responsavel nao encontrado")
    if not usuario.ativo:
        raise HTTPException(409, "Responsavel inativo")
    if len(set(equipamento_ids)) != len(equipamento_ids):
        raise HTTPException(400, "Equipamentos repetidos")
    equipamentos = []
    for equipamento_id in equipamento_ids:
        equipamento = session.get(Equipamento, equipamento_id)
        if equipamento is None:
            raise HTTPException(404, f"Equipamento {equipamento_id} nao encontrado")
        if equipamento.laboratorio_id != laboratorio_id:
            raise HTTPException(409, "Equipamento pertence a outro laboratorio")
        equipamentos.append(equipamento)
    return equipamentos
