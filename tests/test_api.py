from datetime import datetime, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine
from app import models
from app.main import app
from app.database import getSession

@pytest.fixture
def cliente():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)

    @event.listens_for(engine, "connect")
    def habilitar_chaves(conexao, registro):
        conexao.execute("PRAGMA foreign_keys=ON")

    SQLModel.metadata.create_all(engine)

    def sessao_teste():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[getSession] = sessao_teste
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)
    engine.dispose()

def cadastrar_base(cliente):
    laboratorio = cliente.post("/laboratorios/", json={"nome": "Laboratorio de Informatica", "localizacao": "Sala 01"})
    assert laboratorio.status_code == 201
    usuario = cliente.post("/usuarios/", json={"nome": "Ana Souza", "email": "ana@universidade.edu"})
    assert usuario.status_code == 201
    equipamento = cliente.post("/equipamentos/", json={
        "nome": "Microscopio Digital", "patrimonio": "PAT-001", "laboratorio_id": laboratorio.json()["id"]
    })
    assert equipamento.status_code == 201
    return laboratorio.json()["id"], usuario.json()["id"], equipamento.json()["id"]

def test_cadastro_e_consulta(cliente):
    lab, usuario, equipamento = cadastrar_base(cliente)
    assert cliente.get(f"/laboratorios/{lab}").status_code == 200
    assert cliente.get(f"/usuarios/{usuario}").status_code == 200
    assert cliente.get(f"/equipamentos/{equipamento}").status_code == 200
    assert cliente.get("/equipamentos/?pagina=1&tamanho_pagina=1").json()["total"] == 1

def test_patrimonio_duplicado(cliente):
    lab, usuario, equipamento = cadastrar_base(cliente)
    resposta = cliente.post("/equipamentos/", json={"nome": "Outro equipamento", "patrimonio": "PAT-001", "laboratorio_id": lab})
    assert resposta.status_code == 409

def test_ficha_tecnica_unica(cliente):
    lab, usuario, equipamento = cadastrar_base(cliente)
    ficha = {"equipamento_id": equipamento, "fabricante": "Dell", "modelo": "Modelo X"}
    assert cliente.post("/equipamentos/fichas-tecnicas/", json=ficha).status_code == 201
    assert cliente.post("/equipamentos/fichas-tecnicas/", json=ficha).status_code == 409

def test_reserva_conflitante_e_disponibilidade(cliente):
    lab, usuario, equipamento = cadastrar_base(cliente)
    inicio = datetime(2026, 12, 3, 14, 0)
    primeiro = {"equipamento_id": equipamento, "usuario_id": usuario,
                "inicio": inicio.isoformat(), "fim": (inicio + timedelta(hours=2)).isoformat()}
    assert cliente.post("/reservas/", json=primeiro).status_code == 201
    segundo = dict(primeiro)
    segundo["inicio"] = (inicio + timedelta(hours=1)).isoformat()
    segundo["fim"] = (inicio + timedelta(hours=3)).isoformat()
    assert cliente.post("/reservas/", json=segundo).status_code == 409
    disponibilidade = cliente.get("/reservas/disponibilidade", params={
        "equipamento_id": equipamento, "inicio": primeiro["inicio"], "fim": primeiro["fim"]
    })
    assert disponibilidade.status_code == 200
    assert disponibilidade.json()["disponivel"] is False

def test_manutencao_bloqueia_reserva(cliente):
    lab, usuario, equipamento = cadastrar_base(cliente)
    inicio = datetime(2026, 12, 3, 14, 0)
    manutencao = {"equipamento_id": equipamento, "descricao": "Manutencao preventiva",
                  "inicio": inicio.isoformat(), "fim": (inicio + timedelta(hours=2)).isoformat()}
    assert cliente.post("/manutencoes/", json=manutencao).status_code == 201
    resposta = cliente.post("/reservas/", json={
        "equipamento_id": equipamento, "usuario_id": usuario,
        "inicio": inicio.isoformat(), "fim": (inicio + timedelta(hours=1)).isoformat()
    })
    assert resposta.status_code == 409

def test_regras_de_exclusao(cliente):
    lab, usuario, equipamento = cadastrar_base(cliente)
    assert cliente.delete(f"/laboratorios/{lab}").status_code == 409

def test_relatorios(cliente):
    lab, usuario, equipamento = cadastrar_base(cliente)
    assert cliente.get("/relatorios/estatisticas/equipamentos-por-laboratorio").status_code == 200
    assert cliente.get("/relatorios/equipamentos-disponiveis", params={
        "inicio": "2026-12-03T14:00:00", "fim": "2026-12-03T16:00:00"
    }).status_code == 200


def test_atualizacao_equipamento_nao_quebra_experimento(cliente):
    laboratorio_id, usuario_id, equipamento_id = cadastrar_base(cliente)
    outro_lab = cliente.post("/laboratorios/", json={
        "nome": "Laboratorio de Quimica", "localizacao": "Sala 02"
    }).json()["id"]
    exp = cliente.post("/experimentos/", json={
        "nome": "Experimento de teste", "laboratorio_id": laboratorio_id,
        "responsavel_id": usuario_id, "equipamento_ids": [equipamento_id]
    })
    assert exp.status_code == 201
    resposta = cliente.patch(f"/equipamentos/{equipamento_id}", json={"laboratorio_id": outro_lab})
    assert resposta.status_code == 409
    assert cliente.get(f"/equipamentos/{equipamento_id}").json()["laboratorio_id"] == laboratorio_id


def test_atualizacao_experimento_nao_quebra_reserva(cliente):
    laboratorio_id, usuario_id, equipamento_id = cadastrar_base(cliente)
    exp = cliente.post("/experimentos/", json={
        "nome": "Experimento de teste", "laboratorio_id": laboratorio_id,
        "responsavel_id": usuario_id, "equipamento_ids": [equipamento_id]
    })
    assert exp.status_code == 201
    experimento_id = exp.json()["id"]
    reserva = cliente.post("/reservas/", json={
        "equipamento_id": equipamento_id, "usuario_id": usuario_id,
        "experimento_id": experimento_id,
        "inicio": "2026-12-05T09:00:00", "fim": "2026-12-05T11:00:00"
    })
    assert reserva.status_code == 201
    resposta = cliente.patch(f"/experimentos/{experimento_id}", json={"equipamento_ids": []})
    assert resposta.status_code == 409
    associados = cliente.get(f"/relatorios/experimentos/{experimento_id}/equipamentos")
    assert associados.status_code == 200
    assert equipamento_id in [e["id"] for e in associados.json()]
