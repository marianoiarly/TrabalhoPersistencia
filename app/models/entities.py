from typing import Optional
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlmodel import SQLModel, Field, Relationship
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
    equipamentos: list["Equipamento"] = Relationship(back_populates="laboratorio")
    experimentos: list["Experimento"] = Relationship(back_populates="laboratorio")

class Usuario(UsuarioBase, table=True):
    __tablename__ = "usuario"
    id: int | None = Field(default=None, primary_key=True)
    reservas: list["Reserva"] = Relationship(back_populates="usuario")
    experimentos: list["Experimento"] = Relationship(back_populates="responsavel")

class Equipamento(EquipamentoBase, table=True):
    __tablename__ = "equipamento"
    id: int | None = Field(default=None, primary_key=True)
    laboratorio: Laboratorio | None = Relationship(back_populates="equipamentos")
    ficha_tecnica: Optional["FichaTecnica"] = Relationship(back_populates="equipamento", sa_relationship_kwargs={"uselist": False})
    reservas: list["Reserva"] = Relationship(back_populates="equipamento")
    manutencoes: list["Manutencao"] = Relationship(back_populates="equipamento")
    experimentos: list["Experimento"] = Relationship(back_populates="equipamentos", link_model=ExperimentoEquipamento)

class FichaTecnica(FichaTecnicaBase, table=True):
    __tablename__ = "ficha_tecnica"
    __table_args__ = (UniqueConstraint("equipamento_id", name="uq_ficha_equipamento"),)
    id: int | None = Field(default=None, primary_key=True)
    equipamento: Equipamento | None = Relationship(back_populates="ficha_tecnica")

class Experimento(ExperimentoBase, table=True):
    __tablename__ = "experimento"
    id: int | None = Field(default=None, primary_key=True)
    laboratorio: Laboratorio | None = Relationship(back_populates="experimentos")
    responsavel: Usuario | None = Relationship(back_populates="experimentos")
    equipamentos: list[Equipamento] = Relationship(back_populates="experimentos", link_model=ExperimentoEquipamento)
    reservas: list["Reserva"] = Relationship(back_populates="experimento")

class Reserva(ReservaBase, table=True):
    __tablename__ = "reserva"
    __table_args__ = (CheckConstraint("fim > inicio", name="ck_reserva_periodo"),)
    id: int | None = Field(default=None, primary_key=True)
    equipamento: Equipamento | None = Relationship(back_populates="reservas")
    usuario: Usuario | None = Relationship(back_populates="reservas")
    experimento: Experimento | None = Relationship(back_populates="reservas")

class Manutencao(ManutencaoBase, table=True):
    __tablename__ = "manutencao"
    id: int | None = Field(default=None, primary_key=True)
    equipamento: Equipamento | None = Relationship(back_populates="manutencoes")
