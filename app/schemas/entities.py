from datetime import datetime
from sqlmodel import SQLModel, Field

class LaboratorioBase(SQLModel):
    nome: str = Field(min_length=3, max_length=120, index=True)
    localizacao: str = Field(min_length=2, max_length=120)
    descricao: str | None = Field(default=None, max_length=300)
    ativo: bool = True

class LaboratorioCreate(LaboratorioBase):
    pass

class LaboratorioPublic(LaboratorioBase):
    id: int

class LaboratorioUpdate(SQLModel):
    nome: str | None = Field(default=None, min_length=3, max_length=120)
    localizacao: str | None = None
    descricao: str | None = None
    ativo: bool | None = None

class UsuarioBase(SQLModel):
    nome: str = Field(min_length=3, max_length=120, index=True)
    email: str = Field(max_length=120, unique=True)
    ativo: bool = True

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioPublic(UsuarioBase):
    id: int

class UsuarioUpdate(SQLModel):
    nome: str | None = Field(default=None, min_length=3, max_length=120)
    email: str | None = None
    ativo: bool | None = None

class EquipamentoBase(SQLModel):
    nome: str = Field(min_length=3, max_length=120, index=True)
    patrimonio: str = Field(max_length=50, unique=True)
    laboratorio_id: int = Field(foreign_key="laboratorio.id", index=True)
    status: str = Field(default="disponivel", max_length=30, index=True)
    ativo: bool = True

class EquipamentoCreate(EquipamentoBase):
    pass

class EquipamentoPublic(EquipamentoBase):
    id: int

class EquipamentoUpdate(SQLModel):
    nome: str | None = None
    patrimonio: str | None = None
    laboratorio_id: int | None = None
    status: str | None = None
    ativo: bool | None = None

class FichaTecnicaBase(SQLModel):
    equipamento_id: int = Field(foreign_key="equipamento.id", index=True)
    fabricante: str = Field(min_length=2, max_length=120)
    modelo: str = Field(min_length=2, max_length=120)
    numero_serie: str | None = Field(default=None, max_length=100)

class FichaTecnicaCreate(FichaTecnicaBase):
    pass

class FichaTecnicaPublic(FichaTecnicaBase):
    id: int

class FichaTecnicaUpdate(SQLModel):
    fabricante: str | None = None
    modelo: str | None = None
    numero_serie: str | None = None

class ExperimentoBase(SQLModel):
    nome: str = Field(min_length=3, max_length=120)
    descricao: str | None = Field(default=None, max_length=400)
    laboratorio_id: int = Field(foreign_key="laboratorio.id")
    responsavel_id: int = Field(foreign_key="usuario.id")

class ExperimentoCreate(ExperimentoBase):
    equipamento_ids: list[int] = Field(default_factory=list)

class ExperimentoPublic(ExperimentoBase):
    id: int

class ExperimentoUpdate(SQLModel):
    nome: str | None = None
    descricao: str | None = None
    laboratorio_id: int | None = None
    responsavel_id: int | None = None
    equipamento_ids: list[int] | None = None

class ReservaBase(SQLModel):
    equipamento_id: int = Field(foreign_key="equipamento.id", index=True)
    usuario_id: int = Field(foreign_key="usuario.id", index=True)
    experimento_id: int | None = Field(default=None, foreign_key="experimento.id")
    inicio: datetime
    fim: datetime
    status: str = Field(default="ativa", max_length=20)

class ReservaCreate(ReservaBase):
    pass

class ReservaPublic(ReservaBase):
    id: int

class ReservaUpdate(SQLModel):
    equipamento_id: int | None = None
    usuario_id: int | None = None
    experimento_id: int | None = None
    inicio: datetime | None = None
    fim: datetime | None = None
    status: str | None = None

class ManutencaoBase(SQLModel):
    equipamento_id: int = Field(foreign_key="equipamento.id", index=True)
    descricao: str = Field(min_length=3, max_length=300)
    inicio: datetime
    fim: datetime | None = None
    status: str = Field(default="aberta", max_length=20)

class ManutencaoCreate(ManutencaoBase):
    pass

class ManutencaoPublic(ManutencaoBase):
    id: int

class ManutencaoUpdate(SQLModel):
    descricao: str | None = None
    inicio: datetime | None = None
    fim: datetime | None = None
    status: str | None = None
