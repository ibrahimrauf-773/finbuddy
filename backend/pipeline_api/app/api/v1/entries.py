from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.entry import Entry
from app.schemas.entry import EntryCreate
from app.services.posting_composer import PostingComposer, PostingComposerError
from app.schemas.accounting import TransactionIn, LedgerPostIn
from app.repositories.accounting_repo import create_transaction

router = APIRouter(prefix="/v1/entries", tags=["entries"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=dict)
def create_entry(entry_in: EntryCreate, db: Session = Depends(get_db)):
    """
    Creates an Entry record and immediately composes & posts a balanced
    double-entry Transaction + LedgerPosts using the PostingComposer rules.
    """
    # 1) Persist entry
    entry = Entry(
        occurred_on=entry_in.occurred_on,
        activity=entry_in.activity,
        amount_cents=entry_in.amount_cents,
        currency=entry_in.currency,
        notes=entry_in.notes,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    # 2) Compose postings from activity rules
    composer = PostingComposer()
    try:
        posts_raw = composer.compose(
            activity=entry_in.activity,
            amount_cents=entry_in.amount_cents,
        )
    except PostingComposerError as e:
        # If a rule is missing or amount invalid, return a clean 400
        raise HTTPException(status_code=400, detail=str(e))

    # 3) Persist transaction & ledger posts
    tx_in = TransactionIn(
        entry_id=entry.id,
        description=entry_in.notes or entry_in.activity,
        posts=[LedgerPostIn(account=a, side=side, amount_cents=amt)
               for (a, side, amt) in posts_raw],
    )
    tx_out = create_transaction(db, tx_in)

    return {
        "entry_id": entry.id,
        "activity": entry.activity,
        "transaction_id": tx_out.id,
        "posts": [(p.model_dump() if hasattr(p, "model_dump") else p.dict()) for p in tx_out.posts],
    }
