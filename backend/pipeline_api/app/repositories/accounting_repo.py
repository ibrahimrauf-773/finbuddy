from __future__ import annotations
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.accounting import Transaction, LedgerPost
from app.models.entry import Entry  # <-- add this import
from app.schemas.accounting import (
    TransactionIn, TransactionOut, LedgerPostOut, TrialBalanceRow
)
from app.models.accounting import Transaction, LedgerPost
from app.schemas.accounting import LedgerRow

from datetime import date
from typing import Optional, List


def create_transaction(db: Session, tx_in: TransactionIn) -> TransactionOut:
    # Validate balance at the repo as well (defense in depth)
    deb = sum(p.amount_cents for p in tx_in.posts if p.side == "debit")
    cred = sum(p.amount_cents for p in tx_in.posts if p.side == "credit")
    if deb != cred:
        raise ValueError(f"unbalanced posts: debits={deb}, credits={cred}")

    tx = Transaction(entry_id=tx_in.entry_id, description=tx_in.description)
    db.add(tx)
    db.flush()  # get tx.id before creating posts

    for p in tx_in.posts:
        lp = LedgerPost(
            transaction_id=tx.id,
            account=p.account,
            debit_cents=p.amount_cents if p.side == "debit" else 0,
            credit_cents=p.amount_cents if p.side == "credit" else 0,
        )
        db.add(lp)

    db.commit()
    db.refresh(tx)  # loads tx.ledger_posts

    # Manually build the Pydantic output (avoid alias mismatch ledger_posts -> posts)
    posts_out: List[LedgerPostOut] = [
        (LedgerPostOut.model_validate(lp) if hasattr(LedgerPostOut, "model_validate") else LedgerPostOut.from_orm(lp))  # type: ignore[attr-defined]
        for lp in tx.ledger_posts
    ]
    return TransactionOut(
        id=tx.id,
        entry_id=tx.entry_id,
        description=tx.description,
        posts=posts_out,
    )


def trial_balance(db: Session, start: Optional[date] = None, end: Optional[date] = None) -> List[TrialBalanceRow]:
    # ... same filters: q = q.filter(Entry.occurred_on >= start), etc.

    q = (
        db.query(
            LedgerPost.account.label("account"),
            func.coalesce(func.sum(LedgerPost.debit_cents), 0).label("debit"),
            func.coalesce(func.sum(LedgerPost.credit_cents), 0).label("credit"),
        )
        .select_from(LedgerPost)
        .join(Transaction, LedgerPost.transaction_id == Transaction.id)
        .join(Entry, Transaction.entry_id == Entry.id)
    )
    if start:
        q = q.filter(Entry.occurred_on >= start)
    if end:
        q = q.filter(Entry.occurred_on <= end)

    rows = q.group_by(LedgerPost.account).order_by(LedgerPost.account).all()

    out: List[TrialBalanceRow] = []
    for r in rows:
        debit = int(r.debit or 0)
        credit = int(r.credit or 0)
        out.append(TrialBalanceRow(account=r.account, debit_cents=debit, credit_cents=credit, net_cents=debit - credit))
    return out

def ledger_report(db: Session, account: str, start: Optional[date] = None, end: Optional[date] = None) -> List[LedgerRow]:
    # ... same filters

    """
    Per-account ledger, grouped by transaction per day, ordered by date then transaction id.
    """
    q = (
        db.query(
            Entry.occurred_on.label("occurred_on"),
            Transaction.id.label("tx_id"),
            Transaction.description.label("description"),
            func.coalesce(func.sum(LedgerPost.debit_cents), 0).label("debit"),
            func.coalesce(func.sum(LedgerPost.credit_cents), 0).label("credit"),
        )
        .select_from(LedgerPost)
        .join(Transaction, LedgerPost.transaction_id == Transaction.id)
        .join(Entry, Transaction.entry_id == Entry.id)
        .filter(LedgerPost.account == account)
    )
    if start:
        q = q.filter(Entry.occurred_on >= start)
    if end:
        q = q.filter(Entry.occurred_on <= end)

    rows = (
        q.group_by(Entry.occurred_on, Transaction.id, Transaction.description)
         .order_by(Entry.occurred_on.asc(), Transaction.id.asc())
         .all()
    )

    out: List[LedgerRow] = []
    for r in rows:
        out.append(
            LedgerRow(
                occurred_on=str(r.occurred_on),
                description=r.description,
                debit_cents=int(r.debit or 0),
                credit_cents=int(r.credit or 0),
            )
        )
    return out
