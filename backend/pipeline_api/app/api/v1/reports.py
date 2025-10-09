from fastapi import Query, HTTPException
from app.repositories.accounting_repo import trial_balance, ledger_report
from app.schemas.accounting import TrialBalanceRow, TrialBalanceResponse, TrialBalanceTotals, LedgerRow, LedgerResponse, LedgerTotals
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.repositories.accounting_repo import trial_balance
from app.schemas.accounting import TrialBalanceRow

from datetime import date



router = APIRouter(prefix="/v1/reports", tags=["reports"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


from typing import Optional
from app.schemas.accounting import TrialBalanceResponse, TrialBalanceTotals

@router.get("/trial-balance", response_model=list[TrialBalanceRow])
def get_trial_balance(db: Session = Depends(get_db), start: Optional[date] = None, end: Optional[date] = None):
    return trial_balance(db, start, end)

@router.get("/trial-balance/summary", response_model=TrialBalanceResponse)
def get_trial_balance_summary(db: Session = Depends(get_db), start: Optional[date] = None, end: Optional[date] = None):
    rows = trial_balance(db, start, end)
    debit_total = sum(r.debit_cents for r in rows)
    credit_total = sum(r.credit_cents for r in rows)
    return TrialBalanceResponse(
        rows=rows,
        totals=TrialBalanceTotals(
            debit_total=debit_total,
            credit_total=credit_total,
            difference=debit_total - credit_total,
        ),
    )

@router.get("/ledger", response_model=list[LedgerRow])
def get_ledger(
    account: str = Query(..., min_length=1),
    start: Optional[date] = None,   # was Optional[str]
    end: Optional[date] = None,     # was Optional[str]
    db: Session = Depends(get_db),
):
    rows = ledger_report(db, account, start, end)
    if not rows and start is None and end is None:
        return []
    return rows

@router.get("/ledger/summary", response_model=LedgerResponse)
def get_ledger_summary(
    account: str = Query(..., min_length=1),
    start: Optional[date] = None,   # was Optional[str]
    end: Optional[date] = None,     # was Optional[str]
    db: Session = Depends(get_db),
):
    rows = ledger_report(db, account, start, end)
    debit_total = sum(r.debit_cents for r in rows)
    credit_total = sum(r.credit_cents for r in rows)
    return LedgerResponse(
        rows=rows,
        totals=LedgerTotals(
            debit_total=debit_total,
            credit_total=credit_total,
            ending_balance=debit_total - credit_total,
        ),
    )

