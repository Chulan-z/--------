"""manual articles and image support

Revision ID: 20260602_0002
Revises: 20260528_0001
Create Date: 2026-06-02
"""

from alembic import op
import sqlalchemy as sa

revision = "20260602_0002"
down_revision = "20260528_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("news_articles", sa.Column("image_url", sa.String(length=700), nullable=True))
    op.add_column("news_articles", sa.Column("is_featured", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.create_index("ix_articles_is_featured", "news_articles", ["is_featured"])

    op.execute(
        """
        INSERT INTO news_sources (name, url, type, is_active)
        VALUES ('Редакция агрегатора', 'https://local.news/manual', 'api', false)
        ON CONFLICT (url) DO NOTHING
        """
    )


def downgrade() -> None:
    op.drop_index("ix_articles_is_featured", table_name="news_articles")
    op.drop_column("news_articles", "is_featured")
    op.drop_column("news_articles", "image_url")
