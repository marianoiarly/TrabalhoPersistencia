from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlmodel import SQLModel, Field
from app.schemas.entities import (
    LaboratorioBase, UsuarioBase, EquipamentoBase, FichaTecnicaBase,
    ExperimentoBase, ReservaBase, ManutencaoBase
)

class ExperimentoEquipamento(SQLModel, table=True):
    __tablename__ = "experimento_equipamento"
    experimento_id: int = Field(foreign_key="experimento.id", primary_key=True)
    equipamento_id: int = Field(foreign_key="equipamento.id", primary_key=True)

class Laboratorio(LaboratorioBase, table=True):
    __tablename__ = "laboratorio"
    id: int | None = Field(default=None, primary_key=True)

class Usuario(UsuarioBase, table=True):
    __tablename__ = "usuario"
    id: int | None = Field(default=None, primary_key=True)

class Equipamento(EquipamentoBase, table=True):
    __tablename__ = "equipamento"
    id: int | None = Field(default=None, primary_key=True)

class FichaTecnica(FichaTecnicaBase, table=True):
    __tablename__ = "ficha_tecnica"
    __table_args__ = (UniqueConstraint("equipamento_id", name="uq_ficha_equipamento"),)
    id: int | None = Field(default=None, primary_key=True)

class Experimento(ExperimentoBase, table=True):
    __tablename__ = "experimento"
    id: int | None = Field(default=None, primary_key=True)

class Reserva(ReservaBase, table=True):
    __tablename__ = "reserva"
    __table_args__ = (CheckConstraint("fim > inicio", name="ck_reserva_periodo"),)
    id: int | None = Field(default=None, primary_key=True)

class Manutencao(ManutencaoBase, table=True):
    __tablename__ = "manutencao"
    id: int | None = Field(default=None, primary_key=True)
