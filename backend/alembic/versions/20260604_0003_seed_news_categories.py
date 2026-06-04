"""seed readable news categories

Revision ID: 20260604_0003
Revises: 20260602_0002
Create Date: 2026-06-04
"""

from alembic import op

revision = "20260604_0003"
down_revision = "20260602_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for name in [
        "Важная",
        "Мир",
        "Происшествия",
        "Город",
        "Образование",
        "Технологии",
        "Спорт",
        "Культура",
    ]:
        op.execute(f"INSERT INTO categories (name) VALUES ('{name}') ON CONFLICT (name) DO NOTHING")


def downgrade() -> None:
    pass
