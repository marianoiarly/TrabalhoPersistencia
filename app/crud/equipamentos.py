from sqlalchemy import func
from sqlmodel import Session, select
from app.models import Equipamento


def consultar_equipamentos(
    session: Session,
    pagina: int,
    tamanho_pagina: int,
    nome: str | None = None,
    laboratorio_id: int | None = None,
    status: str | None = None,
):
    consulta = select(Equipamento)
    total = select(func.count()).select_from(Equipamento)
    if nome:
        filtro = Equipamento.nome.ilike(f"%{nome}%")
        consulta = consulta.where(filtro)
        total = total.where(filtro)
    if laboratorio_id is not None:
        filtro = Equipamento.laboratorio_id == laboratorio_id
        consulta = consulta.where(filtro)
        total = total.where(filtro)
    if status:
        filtro = Equipamento.status == status
        consulta = consulta.where(filtro)
        total = total.where(filtro)
    quantidade = session.exec(total).one()
    registros = session.exec(
        consulta.order_by(Equipamento.id)
        .offset((pagina - 1) * tamanho_pagina)
        .limit(tamanho_pagina)
    ).all()
    return {
        "dados": registros,
        "total": quantidade,
        "pagina": pagina,
        "tamanho_pagina": tamanho_pagina,
    }
