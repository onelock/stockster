"""change_column_names

Revision ID: 3f366391f567
Revises: 137adf804e11
Create Date: 2026-02-09 13:48:28.720414

"""
from pathlib import Path
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f366391f567'
down_revision: Union[str, Sequence[str], None] = '137adf804e11'
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