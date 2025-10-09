"""
Deterministic mappings from a high-level 'activity' on your Entry
to a set of ledger posts that BALANCE.

Rules you can expand as you add activities.

Example activity payload on Entry (existing table):
{
  "occurred_on": "2025-10-08",
  "activity": "expense_cash",
  "amount_cents": 2599,
  "currency": "USD",
  "notes": "Office coffee"
}
"""

from typing import Dict, List, Tuple

class PostingComposerError(Exception):
    pass


class PostingComposer:
    """
    Minimal rule engine. Extend `activity_map` as you go.
    Returns list of tuples: (account, side, amount_cents)
    """

    # Simple chart-of-accounts naming (you can formalize later)
    # Key = activity
    activity_map: Dict[str, str] = {
        # Expense paid immediately
        "expense_cash": "Dr:Expense:General,Cr:Cash",
        # Sale collected to cash
        "sale_cash": "Dr:Cash,Cr:Revenue:Sales",
        # Record A/P purchase (no cash movement)
        "expense_ap": "Dr:Expense:General,Cr:Accounts Payable",
        # Pay a vendor
        "ap_payment": "Dr:Accounts Payable,Cr:Cash",
    }

    def compose(self, activity: str, amount_cents: int) -> List[Tuple[str, str, int]]:
        if amount_cents <= 0:
            raise PostingComposerError("amount_cents must be > 0")
        mapping = self.activity_map.get(activity)
        if not mapping:
            raise PostingComposerError(f"no posting rule for activity '{activity}'")
        # e.g., "Dr:Expense:General,Cr:Cash"
        parts = [p.strip() for p in mapping.split(",")]
        result: List[Tuple[str, str, int]] = []
        for p in parts:
            side, account = p.split(":", 1)
            side = "debit" if side.lower().startswith("dr") else "credit"
            result.append((account, side, amount_cents))
        return result
