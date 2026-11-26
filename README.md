# Sistema de Gestão de Laboratório

Trabalho Prático 2 da disciplina **Desenvolvimento de Software para Persistência (QXD0099)** — UFC, Campus Quixadá.

**Tema:** Sistema de Gestão de Laboratório  
**Integrantes:** Iarly Batista, André Cayare e Antonio Kaynandeson

## Sobre o projeto

O sistema foi desenvolvido para organizar os laboratórios e seus equipamentos. Pela API, é possível cadastrar laboratórios, usuários, equipamentos, fichas técnicas, experimentos, reservas e manutenções.

A principal funcionalidade é verificar se um equipamento está disponível em determinado período e impedir reservas com horários conflitantes ou durante uma manutenção.

## Tecnologias

Python, FastAPI, SQLModel, SQLite, PostgreSQL e Alembic.

## Entidades e relacionamentos

O projeto possui as seguintes entidades:

- **Laboratório:** nome, localização e situação.
- **Usuário:** nome, e-mail e situação.
- **Equipamento:** nome, patrimônio, laboratório e status.
- **Ficha Técnica:** fabricante, modelo e número de série do equipamento.
- **Experimento:** atividade, laboratório, responsável e equipamentos usados.
- **Reserva:** equipamento, usuário, período e status.
- **Manutenção:** equipamento, descrição, período e status.

A tabela `experimento_equipamento` faz a associação entre experimentos e equipamentos.

Os relacionamentos do sistema são:

- **1:1:** Equipamento — Ficha Técnica.
- **1:N:** Laboratório — Equipamentos.
- **1:N:** Laboratório — Experimentos.
- **1:N:** Usuário — Reservas.
- **1:N:** Usuário — Experimentos (responsável).
- **1:N:** Equipamento — Reservas.
- **1:N:** Equipamento — Manutenções.
- **1:N:** Experimento — Reservas.
- **N:N:** Experimento — Equipamentos, por meio de
  `experimento_equipamento`.
### Modelo relacional

laboratorio(id PK, nome, localizacao, descricao, ativo)
usuario(id PK, nome, email, ativo)
equipamento(id PK, nome, patrimonio, laboratorio_id FK, status, ativo)
ficha_tecnica(id PK, equipamento_id FK UNIQUE, fabricante, modelo, numero_serie)
experimento(id PK, nome, descricao, laboratorio_id FK, responsavel_id FK)
experimento_equipamento(experimento_id PK/FK, equipamento_id PK/FK)
reserva(id PK, equipamento_id FK, usuario_id FK, experimento_id FK,
        inicio, fim, status)
manutencao(id PK, equipamento_id FK, descricao, observacoes,
           inicio, fim, status)

## Como executar

Os comandos abaixo são para o PowerShell, na pasta principal do projeto.

**1. Criar o ambiente virtual e instalar as dependências:**

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install fastapi uvicorn sqlmodel alembic pytest httpx "psycopg[binary]"
```

**2. Configurar o banco:**

A conexão é definida em `app/database.py` pela variável de ambiente `DATABASE_URL`. O SQLite é usado por padrão, mas também é possível selecionar PostgreSQL.

**SQLite (padrão):**

O banco é armazenado no arquivo `laboratorio.db`. Sem a variável `DATABASE_URL`, o sistema utiliza automaticamente:

```text
sqlite:///./laboratorio.db
```

Para configurar explicitamente no PowerShell:

```powershell
$env:DATABASE_URL="sqlite:///./laboratorio.db"
```

**PostgreSQL:**

1. Instale e inicie o servidor PostgreSQL, se ainda não estiver instalado.
2. Pelo pgAdmin (ou pelo `psql`), crie um banco de dados chamado `laboratorio_db`:

```sql
CREATE DATABASE laboratorio_db;
```

3. No PowerShell, na pasta do projeto, configure a conexão (substituindo `SUA_SENHA` pela senha local do seu PostgreSQL):

```powershell
$env:DATABASE_URL="postgresql+psycopg://postgres:SUA_SENHA@localhost:5432/laboratorio_db"
```

O driver `psycopg` é instalado junto das dependências no passo 1. Se o usuário, a porta ou o nome do banco forem diferentes no seu computador, ajuste a URL.

A variável definida com `$env:DATABASE_URL` vale para o terminal atual. Para voltar ao SQLite, configure a URL do SQLite mostrada acima ou remova essa variável do terminal:

```powershell
Remove-Item Env:DATABASE_URL
```

**Não coloque a senha real do banco no README nem a envie para o GitHub.**

Os comandos de migração, povoamento e execução das próximas etapas funcionam para o banco selecionado em `DATABASE_URL`. Aplique as migrações em um banco PostgreSQL novo antes de executar o povoamento.

**3. Criar as tabelas e aplicar as migrações com Alembic:**

Em um banco novo, sem tabelas anteriores:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Se já existir um banco com tabelas criadas antes do Alembic, é preciso conferir a estrutura e a versão antes de aplicar as migrações, para não perder dados.

**4. Inserir os dados iniciais:**

```powershell
.\.venv\Scripts\python.exe -m scripts.povoar
```

**5. Iniciar a API:**

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Acesse o Swagger em: http://127.0.0.1:8000/docs

## Endpoints e filtros

| Rota | O que faz |
| --- | --- |
| `/laboratorios/` | CRUD; filtros por nome e situação |
| `/usuarios/` | CRUD; filtros por nome e situação |
| `/equipamentos/` | CRUD; filtros por nome, laboratório e status; paginação |
| `/equipamentos/fichas-tecnicas/` | Cadastro, consulta, atualização e exclusão de fichas |
| `/experimentos/` | CRUD; filtros por laboratório e responsável |
| `/reservas/` | CRUD; filtros por equipamento, usuário, status e período |
| `/reservas/disponibilidade` | Verifica a disponibilidade em um período |
| `/manutencoes/` | CRUD; filtros por equipamento e status |

Também foram implementadas consultas em `/relatorios/`:

- Reservas de um usuário.
- Histórico de manutenções de um equipamento.
- Equipamentos associados a um experimento.
- Reservas detalhadas, com dados relacionados de outras tabelas.
- Equipamentos disponíveis em um período.
- Quantidade de reservas por equipamento.
- Quantidade de equipamentos por laboratório.

As consultas utilizam relacionamentos, filtros, junções e agregações no banco.
### Funcionalidade específica do tema (F17)

O Sistema de Gestão de Laboratório implementa a verificação de disponibilidade dos equipamentos e o bloqueio de reservas conflitantes.

- **`GET /reservas/disponibilidade`**: verifica se determinado equipamento está disponível em um período, considerando reservas existentes e manutenções abertas.
- **`POST /reservas/`**: realiza o cadastro de reservas, impedindo horários conflitantes, utilização de equipamentos indisponíveis ou em manutenção.

Essa funcionalidade garante maior controle sobre o uso dos equipamentos e evita conflitos de agendamento nos laboratórios.

## Regras de negócio

- A data final da reserva precisa ser posterior à inicial.
- O mesmo equipamento não pode ter duas reservas ativas no mesmo período.
- Não é permitido reservar equipamentos indisponíveis ou em manutenção aberta.
- Usuários e laboratórios inativos não podem participar de novas reservas.
- Os equipamentos de um experimento devem pertencer ao laboratório do experimento.
- O sistema impede exclusões que deixariam registros relacionados inconsistentes.

Quando necessário, a API retorna erros HTTP como `400`, `404`, `409` e `422`.
