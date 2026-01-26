"""initial_schema

Revision ID: 170d8f53ae8e
Revises: 
Create Date: 2026-01-25 17:37:05.349262

SQL-only migration - executes pure SQL files for schema creation.
"""
from typing import Sequence, Union
from pathlib import Path

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '170d8f53ae8e'
down_revision: Union[str, Sequence[str], None] = None
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
    sql = read_sql_file('001_initial_schema_up.sql')
    op.execute(sql)
    print("✅ Initial schema created successfully")


def downgrade() -> None:
    """Downgrade schema by executing SQL file."""
    print("🔄 Rolling back initial schema...")
    sql = read_sql_file('001_initial_schema_down.sql')
    op.execute(sql)
    print("✅ Initial schema rolled back")
