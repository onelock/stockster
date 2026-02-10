"""update_tradings_table

Revision ID: 137adf804e11
Revises: 170d8f53ae8e
Create Date: 2026-02-05 15:56:35.644438

"""
from typing import Sequence, Union
from pathlib import Path

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '137adf804e11'
down_revision: Union[str, Sequence[str], None] = '170d8f53ae8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def read_sql_file(filename: str) -> str:
    """Read SQL file from migrations/sql directory."""
    sql_dir = Path(__file__).parent.parent / 'sql'
    sql_file = sql_dir / filename
    with open(sql_file, 'r') as f:
        return f.read()


def upgrade() -> None:
    """Upgrade schema by executing SQL file."""
    print("🔄 Running initial schema migration...")
    print("📂 Reading SQL file for upgrade...")
    sql = read_sql_file('002_update_tradings_table_up.sql')
    op.execute(sql)
    print("✅ Initial schema created successfully")


def downgrade() -> None:
    """Downgrade schema by executing SQL file."""
    print("🔄 Rolling back initial schema...")
    sql = read_sql_file('002_update_tradings_table_down.sql')
    op.execute(sql)
    print("✅ Initial schema rolled back")
