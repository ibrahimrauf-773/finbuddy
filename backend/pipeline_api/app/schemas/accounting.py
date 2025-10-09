from __future__ import annotations
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

from datetime import date


MoneySide = Literal["debit", "credit"]

# ---------- Inputs ----------
class LedgerPostIn(BaseModel):
    account: str = Field(..., min_length=1, max_length=120)
    side: MoneySide
    amount_cents: int = Field(..., gt=0)

class TransactionIn(BaseModel):
    entry_id: int
    description: Optional[str] = None
    posts: List[LedgerPostIn]

    @field_validator("posts")
    @classmethod
    def posts_must_balance(cls, v: List[LedgerPostIn]):
        deb = sum(p.amount_cents for p in v if p.side == "debit")
        cred = sum(p.amount_cents for p in v if p.side == "credit")
        if deb != cred:
            raise ValueError(f"unbalanced posts: debits={deb}, credits={cred}")
        return v

# ---------- Outputs ----------
class LedgerPostOut(BaseModel):
    id: int
    account: str
    debit_cents: int
    credit_cents: int
    model_config = ConfigDict(from_attributes=True)

class TransactionOut(BaseModel):
    id: int
    entry_id: int
    description: Optional[str]
    posts: List[LedgerPostOut]
    model_config = ConfigDict(from_attributes=True)

class TrialBalanceRow(BaseModel):
    account: str
    debit_cents: int
    credit_cents: int
    net_cents: int  # debit - credit

# ---------- Optional: summary wrapper ----------
class TrialBalanceTotals(BaseModel):
    debit_total: int
    credit_total: int
    difference: int  # debit_total - credit_total (should be 0)

class TrialBalanceResponse(BaseModel):
    rows: List[TrialBalanceRow]
    totals: TrialBalanceTotals

from pydantic import BaseModel

class LedgerRow(BaseModel):
    occurred_on: date          # was str
    description: str | None = None
    debit_cents: int
    credit_cents: int


class LedgerTotals(BaseModel):
    debit_total: int
    credit_total: int
    ending_balance: int  # debit_total - credit_total (debit = +)

class LedgerResponse(BaseModel):
    rows: list[LedgerRow]
    totals: LedgerTotals
