"""
reconcile.py — deterministic reconciliation engine for SettleTrace.

Pure arithmetic with paisa-level (0.01 INR) tolerance. NO LLM calls.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from app.schema import (
    Order,
    SettlementLine,
    BankCredit,
    ReconciliationResult,
    MatchStatus,
    ExceptionReason,
)

# Constants
PAISA_TOLERANCE = 0.01
RAZORPAY_FEE_RATE = 0.02
FEE_VARIANCE_THRESHOLD = 0.15  # 15% variance to flag fee_mismatch
SETTLEMENT_LAG_DAYS = 2  # T+2 is normal, T+3+ is lag
RESERVE_HOLD_MIN = 0.045  # 4.5% (to handle 5% with rounding)
RESERVE_HOLD_MAX = 0.105  # 10.5% (to handle 10% with rounding)

DATA_DIR = Path(__file__).parent.parent / "data"


def load_orders(filepath: Path) -> List[Order]:
    """Load orders from CSV."""
    orders = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            orders.append(Order(
                order_id=row["order_id"],
                order_date=row["order_date"],
                gross_amount=float(row["gross_amount"]),
                currency=row["currency"],
                refunded_amount=float(row["refunded_amount"]),
            ))
    return orders


def load_settlements(filepath: Path) -> List[SettlementLine]:
    """Load settlement lines from CSV."""
    settlements = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            settlements.append(SettlementLine(
                settlement_id=row["settlement_id"],
                order_id=row["order_id"],
                settled_date=row["settled_date"],
                gross_amount=float(row["gross_amount"]),
                razorpay_fee=float(row["razorpay_fee"]),
                gst_on_fee=float(row["gst_on_fee"]),
                net_amount=float(row["net_amount"]),
                is_partial_hold=row["is_partial_hold"].lower() == "true",
                hold_reason=row["hold_reason"] if row["hold_reason"] else None,
            ))
    return settlements


def load_bank_credits(filepath: Path) -> List[BankCredit]:
    """Load bank credits from CSV."""
    credits = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            credits.append(BankCredit(
                credit_id=row["credit_id"],
                value_date=row["value_date"],
                utr=row["utr"],
                amount=float(row["amount"]),
                raw_narration=row["raw_narration"],
            ))
    return credits


def extract_batch_id(settlement_id: str) -> str:
    """Extract batch ID from settlement ID (e.g., SETT-BATCH001-ORD0001 -> BATCH001)."""
    parts = settlement_id.split("-")
    if len(parts) >= 2:
        return parts[1]
    return "UNKNOWN"


def date_diff_days(date1_str: str, date2_str: str) -> int:
    """Calculate days between two ISO date strings."""
    d1 = datetime.fromisoformat(date1_str)
    d2 = datetime.fromisoformat(date2_str)
    return abs((d2 - d1).days)


def check_fee_accuracy(gross: float, actual_fee: float) -> Tuple[bool, float]:
    """
    Check if fee is within acceptable variance of expected 2%.
    Returns (is_accurate, variance_pct).
    """
    expected_fee = round(gross * RAZORPAY_FEE_RATE, 2)
    if expected_fee == 0:
        return True, 0.0
    variance = abs(actual_fee - expected_fee) / expected_fee
    return variance <= FEE_VARIANCE_THRESHOLD, variance


def run_reconciliation(
    orders: List[Order],
    settlements: List[SettlementLine],
    bank_credits: List[BankCredit],
) -> List[ReconciliationResult]:
    """
    Core reconciliation logic.
    
    Returns a ReconciliationResult for every order.
    """
    results: List[ReconciliationResult] = []
    
    # Build lookups
    order_map = {o.order_id: o for o in orders}
    settlement_map = {s.order_id: s for s in settlements}
    
    # Group settlements by batch
    batch_settlements: Dict[str, List[SettlementLine]] = defaultdict(list)
    for s in settlements:
        batch_id = extract_batch_id(s.settlement_id)
        batch_settlements[batch_id].append(s)
    
    # Group bank credits by batch (inferred from narration or matched by UTR)
    # We'll match by searching for BATCH_ID in narration
    batch_credits: Dict[str, List[BankCredit]] = defaultdict(list)
    unmatched_credits: List[BankCredit] = []
    
    for bc in bank_credits:
        matched = False
        for batch_id in batch_settlements.keys():
            if batch_id in bc.raw_narration:
                batch_credits[batch_id].append(bc)
                matched = True
                break
        if not matched:
            unmatched_credits.append(bc)
    
    # Track which bank credits have been used
    used_credit_ids = set()
    
    # Process each order
    for order in orders:
        audit_trail = []
        audit_trail.append(f"Processing order {order.order_id}")
        
        # Get settlement line
        settlement = settlement_map.get(order.order_id)
        if not settlement:
            results.append(ReconciliationResult(
                order_id=order.order_id,
                status=MatchStatus.needs_review,
                matched_settlement_id=None,
                matched_bank_credit_id=None,
                expected_net=0.0,
                actual_net=0.0,
                delta=0.0,
                exception_reason=ExceptionReason.unknown,
                llm_explanation="No settlement line found for this order",
                cited_rule="",
                confidence=1.0,
                audit_trail=audit_trail,
            ))
            continue
        
        audit_trail.append(f"Found settlement {settlement.settlement_id}")
        
        # Check individual order fee accuracy
        fee_accurate, fee_variance = check_fee_accuracy(
            order.gross_amount, 
            settlement.razorpay_fee
        )
        
        if not fee_accurate:
            audit_trail.append(
                f"Fee mismatch detected: expected ~{round(order.gross_amount * RAZORPAY_FEE_RATE, 2)}, "
                f"actual {settlement.razorpay_fee} (variance {fee_variance:.1%})"
            )
            results.append(ReconciliationResult(
                order_id=order.order_id,
                status=MatchStatus.needs_review,
                matched_settlement_id=settlement.settlement_id,
                matched_bank_credit_id=None,
                expected_net=round(order.gross_amount * (1 - RAZORPAY_FEE_RATE * 1.18), 2),
                actual_net=settlement.net_amount,
                delta=settlement.net_amount - round(order.gross_amount * (1 - RAZORPAY_FEE_RATE * 1.18), 2),
                exception_reason=ExceptionReason.fee_mismatch,
                llm_explanation=f"Fee variance {fee_variance:.1%} exceeds threshold {FEE_VARIANCE_THRESHOLD:.1%}",
                cited_rule="Standard Razorpay fee: 2% + 18% GST",
                confidence=1.0,
                audit_trail=audit_trail,
            ))
            continue
        
        # Get batch ID and batch settlements
        batch_id = extract_batch_id(settlement.settlement_id)
        batch_lines = batch_settlements[batch_id]
        
        # Calculate expected batch net
        expected_batch_net = sum(s.net_amount for s in batch_lines)
        audit_trail.append(
            f"Batch {batch_id}: {len(batch_lines)} orders, "
            f"expected net ₹{expected_batch_net:,.2f}"
        )
        
        # Get bank credits for this batch
        credits = batch_credits.get(batch_id, [])
        
        if not credits:
            audit_trail.append("No bank credit found for this batch")
            results.append(ReconciliationResult(
                order_id=order.order_id,
                status=MatchStatus.unresolved,
                matched_settlement_id=settlement.settlement_id,
                matched_bank_credit_id=None,
                expected_net=settlement.net_amount,
                actual_net=0.0,
                delta=-settlement.net_amount,
                exception_reason=ExceptionReason.missing_bank_credit,
                llm_explanation="No bank credit found matching this settlement batch",
                cited_rule="",
                confidence=1.0,
                audit_trail=audit_trail,
            ))
            continue
        
        # Check for duplicate credits (same UTR)
        if len(credits) > 1:
            utrs = [c.utr for c in credits]
            if len(set(utrs)) < len(utrs):
                audit_trail.append(f"Duplicate bank credits detected: {len(credits)} credits with overlapping UTRs")
                # Pick the first credit for matching
                credit = credits[0]
                used_credit_ids.add(credit.credit_id)
                results.append(ReconciliationResult(
                    order_id=order.order_id,
                    status=MatchStatus.needs_review,
                    matched_settlement_id=settlement.settlement_id,
                    matched_bank_credit_id=credit.credit_id,
                    expected_net=settlement.net_amount,
                    actual_net=credit.amount / len(batch_lines),  # pro-rata
                    delta=(credit.amount / len(batch_lines)) - settlement.net_amount,
                    exception_reason=ExceptionReason.duplicate_batch,
                    llm_explanation=f"Multiple bank credits found for batch {batch_id}",
                    cited_rule="",
                    confidence=0.7,
                    audit_trail=audit_trail,
                ))
                continue
        
        # Single credit (normal case)
        credit = credits[0]
        used_credit_ids.add(credit.credit_id)
        actual_batch_net = credit.amount
        delta_batch = actual_batch_net - expected_batch_net
        
        audit_trail.append(
            f"Bank credit {credit.credit_id}: ₹{actual_batch_net:,.2f} "
            f"on {credit.value_date}"
        )
        audit_trail.append(f"Delta: ₹{delta_batch:,.2f}")
        
        # Check settlement timing
        days_to_credit = date_diff_days(settlement.settled_date, credit.value_date)
        audit_trail.append(f"Settlement to credit: {days_to_credit} days")
        
        # Decision logic
        status = MatchStatus.matched
        exception_reason = None
        explanation = "Perfect match"
        confidence = 1.0
        
        # Check if within tolerance
        if abs(delta_batch) <= PAISA_TOLERANCE:
            if days_to_credit > SETTLEMENT_LAG_DAYS:
                status = MatchStatus.settlement_lag
                exception_reason = ExceptionReason.settlement_lag
                explanation = (
                    f"Amount matches but bank credit arrived {days_to_credit} days "
                    f"after settlement date (normal window: T+{SETTLEMENT_LAG_DAYS})"
                )
                audit_trail.append(f"Status: settlement_lag ({days_to_credit} days after settlement)")
            else:
                # Genuine clean match
                audit_trail.append("Status: matched (amount within ₹0.01 tolerance, timing T+1/T+2)")
        else:
            # Check for partial hold pattern (5-10% withheld AND settlement marked with hold)
            if delta_batch < 0:  # short credit
                shortage_pct = abs(delta_batch) / expected_batch_net
                # Only classify as partial_hold if BOTH conditions are true:
                # 1. Shortage is in 5-10% range (reserve-hold convention)
                # 2. Settlement line explicitly marked is_partial_hold=True
                # This prevents false positives where refund shortfalls happen to land in the same range
                if (RESERVE_HOLD_MIN <= shortage_pct <= RESERVE_HOLD_MAX and 
                    settlement.is_partial_hold):
                    status = MatchStatus.partial_hold
                    exception_reason = ExceptionReason.partial_hold
                    explanation = (
                        f"Reserve hold detected: ₹{abs(delta_batch):,.2f} "
                        f"({shortage_pct:.1%}) withheld from batch net"
                    )
                    audit_trail.append(
                        f"Status: partial_hold — {shortage_pct:.1%} withheld "
                        f"(₹{abs(delta_batch):,.2f})"
                    )
                else:
                    # Unexplained shortage — likely refund netted in same cycle, or hold without flag
                    status = MatchStatus.needs_review
                    exception_reason = ExceptionReason.refund_not_netted
                    explanation = (
                        f"Bank credit short by ₹{abs(delta_batch):,.2f} ({shortage_pct:.1%}) "
                        f"— outside reserve-hold pattern or settlement not marked with hold; "
                        f"possible refund netted in batch or manual adjustment"
                    )
                    audit_trail.append(
                        f"Status: needs_review — shortage ₹{abs(delta_batch):,.2f} "
                        f"({shortage_pct:.1%}), not confirmed as reserve hold"
                    )
            else:
                # Excess credit — unexpected
                status = MatchStatus.needs_review
                exception_reason = ExceptionReason.unknown
                explanation = (
                    f"Bank credit exceeds expected batch net by ₹{delta_batch:,.2f} "
                    f"— possible duplicate or misrouted credit"
                )
                audit_trail.append(
                    f"Status: needs_review — excess of ₹{delta_batch:,.2f} "
                    f"has no known cause"
                )
        
        # Calculate per-order expected net
        expected_net = settlement.net_amount
        # Pro-rata actual net (divide batch credit by number of orders)
        actual_net = actual_batch_net / len(batch_lines)
        delta = actual_net - expected_net
        
        results.append(ReconciliationResult(
            order_id=order.order_id,
            status=status,
            matched_settlement_id=settlement.settlement_id,
            matched_bank_credit_id=credit.credit_id,
            expected_net=expected_net,
            actual_net=actual_net,
            delta=delta,
            exception_reason=exception_reason,
            llm_explanation=explanation,
            cited_rule="Razorpay fee: 2% + 18% GST; Settlement: T+1 to T+2",
            confidence=confidence,
            audit_trail=audit_trail,
        ))
    
    # Handle orphan credits
    for credit in unmatched_credits:
        audit_trail = [
            f"Orphan bank credit detected: {credit.credit_id}",
            f"Amount: ₹{credit.amount:,.2f}, Date: {credit.value_date}",
            f"Narration: {credit.raw_narration}",
            "No matching settlement batch found",
        ]
        # Create a pseudo-result for tracking
        results.append(ReconciliationResult(
            order_id=f"ORPHAN-{credit.credit_id}",
            status=MatchStatus.unresolved,
            matched_settlement_id=None,
            matched_bank_credit_id=credit.credit_id,
            expected_net=0.0,
            actual_net=credit.amount,
            delta=credit.amount,
            exception_reason=ExceptionReason.orphan_bank_credit,
            llm_explanation=f"Bank credit with no matching settlement: {credit.raw_narration}",
            cited_rule="",
            confidence=0.9,
            audit_trail=audit_trail,
        ))
    
    return results


def print_summary(results: List[ReconciliationResult]) -> None:
    """Print reconciliation summary — every non-matched status shows its exception_reason."""
    order_results = [r for r in results if not r.order_id.startswith("ORPHAN-")]

    status_counts: Dict[str, int] = defaultdict(int)
    # Per-status breakdown of exception_reasons
    status_exception_map: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for r in results:
        status_counts[r.status.value] += 1
        reason_label = r.exception_reason.value if r.exception_reason else "—"
        status_exception_map[r.status.value][reason_label] += 1

    total_orders = len(order_results)
    matched = status_counts.get(MatchStatus.matched.value, 0)
    match_rate = (matched / total_orders * 100) if total_orders > 0 else 0

    print("\n" + "=" * 65)
    print("RECONCILIATION SUMMARY")
    print("=" * 65)
    print(f"Total orders processed : {total_orders}")
    print(f"Matched orders         : {matched} ({match_rate:.1f}%)")
    print()
    print(f"{'Status':<22} {'Count':>5}  {'%':>5}  Exception reason(s)")
    print("-" * 65)
    for status in sorted(status_counts.keys()):
        count = status_counts[status]
        pct = count / len(results) * 100
        reasons = status_exception_map[status]
        # First reason on same line, overflow reasons on continuation lines
        reason_parts = [
            f"{reason} ×{cnt}" if cnt > 1 else reason
            for reason, cnt in sorted(reasons.items())
        ]
        first = reason_parts[0] if reason_parts else ""
        print(f"  {status:<20} {count:>5}  {pct:>4.1f}%  {first}")
        for extra in reason_parts[1:]:
            print(f"  {'':20} {'':>5}  {'':>5}  {extra}")
    print("=" * 65)


def main():
    """Run reconciliation on generated data."""
    print("Loading data...")
    orders = load_orders(DATA_DIR / "orders_ledger.csv")
    settlements = load_settlements(DATA_DIR / "razorpay_settlements.csv")
    bank_credits = load_bank_credits(DATA_DIR / "bank_statement.csv")
    
    print(f"Loaded {len(orders)} orders, {len(settlements)} settlements, {len(bank_credits)} bank credits")
    
    print("\nRunning reconciliation...")
    results = run_reconciliation(orders, settlements, bank_credits)
    
    print_summary(results)
    
    # Show a few sample audit trails
    print("\n" + "=" * 60)
    print("SAMPLE AUDIT TRAILS (first 3 orders)")
    print("=" * 60)
    for r in results[:3]:
        print(f"\nOrder: {r.order_id}")
        print(f"Status: {r.status.value}")
        for line in r.audit_trail:
            print(f"  {line}")
    
    return results


if __name__ == "__main__":
    main()
