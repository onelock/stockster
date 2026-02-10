"""change_column_ath_type

Revision ID: 314d5e09938f
Revises: 3f366391f567
Create Date: 2026-02-09 13:50:48.714791

"""
from pathlib import Path
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '314d5e09938f'
down_revision: Union[str, Sequence[str], None] = '3f366391f567'
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
    sql = read_sql_file('003_copy_date_ath_to_one_day_change_up.sql')
    op.execute(sql)
    print("✅ Initial schema created successfully")


def downgrade() -> None:
    """Downgrade schema by executing SQL file."""
    print("🔄 Rolling back initial schema...")
    sql = read_sql_file('003_copy_date_ath_to_one_day_change_down.sql')
    op.execute(sql)
    print("✅ Initial schema rolled back")
