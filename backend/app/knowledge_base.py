"""
knowledge_base.py — reconciliation policy knowledge base for SettleTrace.

The categorization agent MUST cite a KB entry (by id) for every classification
it makes. This module is intentionally deterministic — no embeddings, no network
calls. Swap the retrieve() implementation later without touching any caller.
"""

from __future__ import annotations

from typing import Dict, List

from app.schema import ACCOUNT_CATEGORIES


# ---------------------------------------------------------------------------
# Knowledge base — 8 policy passages
# ---------------------------------------------------------------------------

KB: List[Dict[str, str]] = [
    {
        "id": "kb-001",
        "topic": "settlement_lag",
        "text": (
            "Razorpay typically credits the merchant's bank account within T+1 or T+2 "
            "business days of the settlement date shown in the settlement report. "
            "Credits arriving on T+3 through T+7 are classified as settlement_lag and "
            "should be flagged for monitoring but do not require a debit adjustment. "
            "Credits arriving beyond T+7 must be escalated to Razorpay support with "
            "the UTR reference for manual reconciliation."
        ),
    },
    {
        "id": "kb-002",
        "topic": "partial_hold",
        "text": (
            "Razorpay may withhold a reserve amount of 5% to 10% of a settlement batch's "
            "net payout as a risk reserve, particularly for new merchants or those with "
            "elevated chargeback ratios. The withheld amount is recorded under "
            "'Settlement Reserve (Held)' in the GL and released after the reserve period "
            "(typically 7–15 days). A bank credit that is short by 5–10% of the expected "
            "batch net, with the settlement line marked is_partial_hold=True, should be "
            "classified as partial_hold — not as a discrepancy requiring investigation."
        ),
    },
    {
        "id": "kb-003",
        "topic": "fee_mismatch",
        "text": (
            "The standard Razorpay processing fee is 2% of the gross transaction amount, "
            "with 18% GST charged on top of that fee (effective total deduction ≈ 2.36%). "
            "Merchants on a custom pricing tier may have a negotiated rate, but any "
            "per-order fee that deviates from the contracted rate by more than 15% must "
            "be flagged as fee_mismatch for manual review. GST is non-negotiable and must "
            "always equal 18% of the applied fee, regardless of tier; a GST deviation "
            "alone is classified as gst_mismatch."
        ),
    },
    {
        "id": "kb-004",
        "topic": "refund_not_netted",
        "text": (
            "Razorpay nets refunds within the same settlement cycle: a refund processed "
            "before the settlement cut-off is subtracted from the batch net payout rather "
            "than issued as a separate credit. If the bank credit for a batch is short by "
            "an amount that does not match the 5–10% reserve-hold pattern, the shortfall "
            "is likely a refund that was netted in the same cycle but not reflected in the "
            "orders ledger. This should be classified as refund_not_netted and the refund "
            "transaction should be located in the Razorpay dashboard for reconciliation."
        ),
    },
    {
        "id": "kb-005",
        "topic": "duplicate_batch",
        "text": (
            "A duplicate batch occurs when the bank statement shows two credits carrying "
            "the same UTR (Unique Transaction Reference) for the same settlement batch. "
            "This can happen due to a bank retry after a failed credit or a Razorpay "
            "system error. Duplicate UTR credits must never be auto-recognised as "
            "additional revenue; both entries must be flagged as duplicate_batch, the "
            "excess credit placed in 'Unreconciled Suspense', and a reversal requested "
            "from the bank. Human review is mandatory before any GL posting."
        ),
    },
    {
        "id": "kb-006",
        "topic": "orphan_bank_credit",
        "text": (
            "An orphan bank credit is a credit entry on the bank statement that has no "
            "corresponding settlement batch in the Razorpay settlement report. Common "
            "causes include manual adjustments by Razorpay, misrouted NEFT/RTGS payments, "
            "or credits belonging to a different merchant account. Orphan credits must "
            "never be auto-categorised as sales revenue; they must be parked under "
            "'Unreconciled Suspense' in the GL until the source is confirmed in writing "
            "from Razorpay or the remitting bank."
        ),
    },
    {
        "id": "kb-007",
        "topic": "currency_rounding",
        "text": (
            "When a settlement batch net is apportioned across individual orders, "
            "floating-point division may produce per-order amounts that differ from the "
            "batch total by a few paise (up to ±0.05 INR per order). These sub-paisa "
            "residuals are classified as currency_rounding and should be absorbed into "
            "the 'Bank Charges' GL account at period-end rather than flagged as "
            "discrepancies. The reconciliation engine uses a paisa-level tolerance "
            "(0.01 INR) at the batch level, so rounding errors never affect batch-level "
            "match status."
        ),
    },
    {
        "id": "kb-008",
        "topic": "gl_account_mapping",
        "text": (
            "All GL postings must use the closed chart of accounts defined in the system. "
            "The authorised account names are: "
            + ", ".join(f'"{a}"' for a in ACCOUNT_CATEGORIES)
            + ". "
            "Any GL export entry whose account field does not exactly match one of these "
            "names (including common variants such as 'SALES-ONLINE', 'Sales : Online', "
            "'RAZORPAY-FEE', 'GST-INPUT', etc.) must be normalised before posting. "
            "The reconciliation agent must map dirty account strings to the nearest "
            "authorised name and record the original and normalised values in the "
            "audit trail."
        ),
    },
]

# Pre-build a topic index for O(1) lookup
_TOPIC_INDEX: Dict[str, List[Dict[str, str]]] = {}
for _entry in KB:
    _TOPIC_INDEX.setdefault(_entry["topic"], []).append(_entry)


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------

def retrieve(topic: str, top_k: int = 1) -> List[Dict[str, str]]:
    """
    Return up to top_k KB entries whose topic exactly matches the given string.

    This is intentionally a deterministic exact-match lookup — no embeddings,
    no fuzzy search. The implementation is swappable later (e.g., replace with
    a vector-store call) without changing any caller signature.

    Parameters
    ----------
    topic : str
        One of: settlement_lag, partial_hold, fee_mismatch, refund_not_netted,
        duplicate_batch, orphan_bank_credit, currency_rounding, gl_account_mapping.
    top_k : int
        Maximum number of passages to return (default 1).

    Returns
    -------
    List of matching passage dicts (may be empty if topic not found).
    Each dict has keys: id, topic, text.
    """
    matches = _TOPIC_INDEX.get(topic, [])
    return matches[:top_k]


def retrieve_by_id(kb_id: str) -> Dict[str, str] | None:
    """Return a single KB entry by its id (e.g. 'kb-003'), or None."""
    for entry in KB:
        if entry["id"] == kb_id:
            return entry
    return None


def all_topics() -> List[str]:
    """Return the list of all topics covered by the KB."""
    return list(_TOPIC_INDEX.keys())
