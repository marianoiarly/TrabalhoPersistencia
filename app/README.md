# Sistema de Gestao de Laboratorio

Trabalho Pratico 2 - QXD0099 - Desenvolvimento de Software para Persistencia - UFC Quixada.

**Tema 19:** verificar a disponibilidade de equipamentos e impedir reservas conflitantes.

**Integrantes:** preencher com os tres integrantes da equipe.

## Tecnologias

Python, FastAPI, SQLModel, PostgreSQL, SQLite, Alembic, Pytest.

## Modelagem

Entidades principais: Laboratorio, Usuario, Equipamento, Experimento, Reserva e Manutencao. Entidades auxiliares: FichaTecnica e ExperimentoEquipamento.

- 1:1: Equipamento e FichaTecnica (equipamento_id unico).
- 1:N: Laboratorio e Equipamento; Usuario e Reserva; Equipamento e Manutencao.
- N:N: Experimento e Equipamento, pela tabela associativa ExperimentoEquipamento.

Chaves primarias e estrangeiras sao definidas nos modelos SQLModel; Reserva possui restricao de periodo e FichaTecnica possui unicidade de equipamento.

## Ambiente

No PowerShell, dentro da pasta do repositorio:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install fastapi uvicorn sqlmodel "psycopg[binary]" alembic pytest httpx
```

## Bancos de dados

No PostgreSQL, criar o banco `laboratorio_db` com pgAdmin ou SQL. No PowerShell, configurar a conexao sem gravar senha no repositorio:

```powershell
$env:DATABASE_URL = "postgresql+psycopg://postgres:SUA_SENHA@localhost:5432/laboratorio_db"
```

Para SQLite, no mesmo terminal:

```powershell
$env:DATABASE_URL = "sqlite:///./laboratorio.db"
```

O banco principal e PostgreSQL. O ORM permite alternar para SQLite pela variavel `DATABASE_URL`, sem mudar os routers ou os modelos.

## Migracoes com Alembic

Se o banco estiver **vazio e sem tabelas**, executar:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Se o banco **ja tiver todas as tabelas da etapa anterior e ainda nao tiver a coluna `observacoes` em `manutencao`**, preservar os dados e executar:

```powershell
.\.venv\Scripts\python.exe -m alembic stamp 01_estrutura_inicial
.\.venv\Scripts\python.exe -m alembic upgrade head
```

O primeiro comando apenas marca o esquema inicial ja existente. O segundo aplica uma alteracao real sem excluir as tabelas: acrescenta `observacoes` a `manutencao`. Nao executar `stamp` em banco vazio ou esquema diferente. Se nao souber a situacao do banco, conferir as tabelas antes de prosseguir.

## Executar a API

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Documentacao interativa: http://127.0.0.1:8000/docs

## Povoamento e testes

Com as migracoes aplicadas:

```powershell
.\.venv\Scripts\python.exe -m scripts.povoar
.\.venv\Scripts\python.exe -m pytest tests/test_api.py -v
```

O povoamento insere 10 equipamentos e registros relacionados. Os testes usam SQLite em memoria, independentemente da conexao principal.

## Rotas e filtros

- `/laboratorios/`: CRUD; filtros `nome` e `ativo`.
- `/usuarios/`: CRUD; filtros `nome` e `ativo`.
- `/equipamentos/`: CRUD; filtros `nome`, `laboratorio_id`, `status`; `pagina` e `tamanho_pagina` no banco.
- `/equipamentos/fichas-tecnicas/`: cadastro e consultas da ficha tecnica 1:1.
- `/experimentos/`: CRUD, associacao com equipamentos e filtros por laboratorio e responsavel.
- `/manutencoes/`: CRUD; filtros de equipamento e status.
- `/reservas/`: CRUD; filtros de equipamento, usuario, status e intervalo de datas.
- `/reservas/disponibilidade`: recebe equipamento, inicio e fim; retorna disponibilidade real.
- `/relatorios/usuarios/{id}/reservas`: reservas do usuario.
- `/relatorios/equipamentos/{id}/manutencoes`: historico de manutencoes.
- `/relatorios/experimentos/{id}/equipamentos`: equipamentos vinculados ao experimento.
- `/relatorios/reservas-detalhadas`: JOIN de reservas, usuarios, equipamentos e laboratorios.
- `/relatorios/equipamentos-disponiveis`: consulta com filtros de periodo, reservas e manutencoes.
- `/relatorios/estatisticas/reservas-por-equipamento`: agregacao COUNT e GROUP BY.
- `/relatorios/estatisticas/equipamentos-por-laboratorio`: agregacao COUNT e GROUP BY.

## Regras de negocio

1. Uma reserva precisa ter fim posterior ao inicio.
2. O mesmo equipamento nao aceita reservas ativas em periodos sobrepostos.
3. Equipamentos indisponiveis ou em manutencao aberta nao podem ser reservados no periodo.
4. Usuarios e laboratorios inativos nao podem participar de novas reservas.
5. Um equipamento precisa pertencer ao laboratorio de um experimento antes de ser associado.
6. Exclusoes com dependencias relevantes sao bloqueadas.

HTTP: 201 para cadastro, 200 para consulta, 204 para exclusao, 400 para regra invalida, 404 para recurso inexistente, 409 para conflito, 422 para validacao, 500 para erro interno. Erros internos de banco nao sao expostos como mensagem ao usuario.

## Demonstracao

Apresentar no Swagger cadastro, listagem, atualizacao e exclusao; paginacao e filtros; 1:1, 1:N e N:N; tres consultas relacionadas; duas consultas complexas; agregacoes; tres ou mais regras de negocio; disponibilidade e conflitos; mudanca de banco e migracao Alembic preservando registros.
