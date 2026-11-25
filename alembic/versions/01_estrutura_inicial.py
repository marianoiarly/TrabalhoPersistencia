from alembic import op
import sqlalchemy as sa

revision = "01_estrutura_inicial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "laboratorio",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(120), nullable=False),
        sa.Column("localizacao", sa.String(120), nullable=False),
        sa.Column("descricao", sa.String(300), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_laboratorio_nome", "laboratorio", ["nome"])
    op.create_table(
        "usuario",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(120), nullable=False),
        sa.Column("email", sa.String(120), nullable=False, unique=True),
        sa.Column("ativo", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_usuario_nome", "usuario", ["nome"])
    op.create_table(
        "equipamento",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(120), nullable=False),
        sa.Column("patrimonio", sa.String(50), nullable=False, unique=True),
        sa.Column(
            "laboratorio_id",
            sa.Integer(),
            sa.ForeignKey("laboratorio.id"),
            nullable=False,
        ),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_equipamento_nome", "equipamento", ["nome"])
    op.create_index("ix_equipamento_laboratorio_id", "equipamento", ["laboratorio_id"])
    op.create_index("ix_equipamento_status", "equipamento", ["status"])
    op.create_table(
        "ficha_tecnica",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "equipamento_id",
            sa.Integer(),
            sa.ForeignKey("equipamento.id"),
            nullable=False,
        ),
        sa.Column("fabricante", sa.String(120), nullable=False),
        sa.Column("modelo", sa.String(120), nullable=False),
        sa.Column("numero_serie", sa.String(100), nullable=True),
        sa.UniqueConstraint("equipamento_id", name="uq_ficha_equipamento"),
    )
    op.create_index(
        "ix_ficha_tecnica_equipamento_id", "ficha_tecnica", ["equipamento_id"]
    )
    op.create_table(
        "experimento",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(120), nullable=False),
        sa.Column("descricao", sa.String(400), nullable=True),
        sa.Column(
            "laboratorio_id",
            sa.Integer(),
            sa.ForeignKey("laboratorio.id"),
            nullable=False,
        ),
        sa.Column(
            "responsavel_id", sa.Integer(), sa.ForeignKey("usuario.id"), nullable=False
        ),
    )
    op.create_table(
        "experimento_equipamento",
        sa.Column(
            "experimento_id",
            sa.Integer(),
            sa.ForeignKey("experimento.id"),
            primary_key=True,
        ),
        sa.Column(
            "equipamento_id",
            sa.Integer(),
            sa.ForeignKey("equipamento.id"),
            primary_key=True,
        ),
    )
    op.create_table(
        "manutencao",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "equipamento_id",
            sa.Integer(),
            sa.ForeignKey("equipamento.id"),
            nullable=False,
        ),
        sa.Column("descricao", sa.String(300), nullable=False),
        sa.Column("inicio", sa.DateTime(), nullable=False),
        sa.Column("fim", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
    )
    op.create_index("ix_manutencao_equipamento_id", "manutencao", ["equipamento_id"])
    op.create_table(
        "reserva",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "equipamento_id",
            sa.Integer(),
            sa.ForeignKey("equipamento.id"),
            nullable=False,
        ),
        sa.Column(
            "usuario_id", sa.Integer(), sa.ForeignKey("usuario.id"), nullable=False
        ),
        sa.Column(
            "experimento_id",
            sa.Integer(),
            sa.ForeignKey("experimento.id"),
            nullable=True,
        ),
        sa.Column("inicio", sa.DateTime(), nullable=False),
        sa.Column("fim", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.CheckConstraint("fim > inicio", name="ck_reserva_periodo"),
    )
    op.create_index("ix_reserva_equipamento_id", "reserva", ["equipamento_id"])
    op.create_index("ix_reserva_usuario_id", "reserva", ["usuario_id"])


def downgrade():
    op.drop_table("reserva")
    op.drop_table("manutencao")
    op.drop_table("experimento_equipamento")
    op.drop_table("experimento")
    op.drop_table("ficha_tecnica")
    op.drop_table("equipamento")
    op.drop_table("usuario")
    op.drop_table("laboratorio")
