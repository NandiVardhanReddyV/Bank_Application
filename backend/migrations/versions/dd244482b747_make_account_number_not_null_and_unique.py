"""make account_number not null and unique

Revision ID: dd244482b747
Revises: 33e51967017d
Create Date: 2026-03-14 19:57:32.031355

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dd244482b747'
down_revision: Union[str, Sequence[str], None] = '33e51967017d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('accounts','account_number',
                    existing_type = sa.String(length = 20),
                    nullable = False #key change
                    )
    #op.create_unique_constraint('uq_account_number', 'accounts', ['account_number'])
    


def downgrade() -> None:
    """Downgrade schema."""
    """ Reverse - make account_number nullable again."""
    op.drop_constraint('uq_account_number', 'accounts')
    op.alter_column('accounts','account_number',
                    existing_type = sa.String(length = 20),
                    nullable = True     # <- reverse of upgrade
    )
