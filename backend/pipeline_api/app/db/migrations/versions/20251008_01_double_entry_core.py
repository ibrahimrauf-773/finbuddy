"""double-entry core: transactions + ledger_posts

Revision ID: 20251008_01
Revises: <PUT_PREVIOUS_REVISION_ID_HERE>
Create Date: 2025-10-08
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20251008_01"
down_revision = "<PUT_PREVIOUS_REVISION_ID_HERE>"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entry_id", sa.Integer(), nullable=False, index=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_transactions_entry_id", "transactions", ["entry_id"])

    op.create_foreign_key(
        "fk_transactions_entry_id",
        "transactions",
        "entries",
        ["entry_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_table(
        "ledger_posts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("transaction_id", sa.Integer(), nullable=False, index=True),
        sa.Column("account", sa.String(length=120), nullable=False, index=True),
        sa.Column("debit_cents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("credit_cents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("debit_cents >= 0 AND credit_cents >= 0", name="ck_lp_nonneg"),
        sa.CheckConstraint("NOT (debit_cents > 0 AND credit_cents > 0)", name="ck_lp_one_side_only"),
        sa.CheckConstraint("(debit_cents > 0) OR (credit_cents > 0)", name="ck_lp_at_least_one"),
    )
    op.create_index("ix_ledger_posts_transaction_id", "ledger_posts", ["transaction_id"])
    op.create_index("ix_ledger_posts_account", "ledger_posts", ["account"])

    op.create_foreign_key(
        "fk_ledger_posts_tx_id",
        "ledger_posts",
        "transactions",
        ["transaction_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade():
    op.drop_constraint("fk_ledger_posts_tx_id", "ledger_posts", type_="foreignkey")
    op.drop_index("ix_ledger_posts_account", table_name="ledger_posts")
    op.drop_index("ix_ledger_posts_transaction_id", table_name="ledger_posts")
    op.drop_table("ledger_posts")

    op.drop_constraint("fk_transactions_entry_id", "transactions", type_="foreignkey")
    op.drop_index("ix_transactions_entry_id", table_name="transactions")
    op.drop_table("transactions")
