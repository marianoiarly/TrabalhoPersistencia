from alembic import op
import sqlalchemy as sa

revision = "02_observacoes_manutencao"
down_revision = "01_estrutura_inicial"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("manutencao", sa.Column("observacoes", sa.String(300), nullable=True))


def downgrade():
    op.drop_column("manutencao", "observacoes")
