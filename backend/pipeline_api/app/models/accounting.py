from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey, CheckConstraint
from app.db.session import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    entry_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("entries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    ledger_posts = relationship(
        "LedgerPost",
        back_populates="transaction",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

class LedgerPost(Base):
    __tablename__ = "ledger_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    transaction_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("transactions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    account: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    debit_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    credit_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    transaction = relationship("Transaction", back_populates="ledger_posts")

    __table_args__ = (
        CheckConstraint("debit_cents >= 0 AND credit_cents >= 0", name="ck_lp_nonneg"),
        CheckConstraint("NOT (debit_cents > 0 AND credit_cents > 0)", name="ck_lp_one_side_only"),
        CheckConstraint("(debit_cents > 0) OR (credit_cents > 0)", name="ck_lp_at_least_one"),
    )
