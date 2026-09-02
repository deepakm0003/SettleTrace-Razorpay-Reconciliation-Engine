"""
generate_data.py — synthetic data generator for SettleTrace.

Creates 65 orders grouped into batches of 6, with ONE scenario per batch.
Outputs 4 CSVs + ground_truth.json for evaluation.

Scenario weights:
- clean: 45%
- partial_hold: 12% (5% reserve withheld)
- settlement_lag: 12% (bank credit T+5 instead of T+1/T+2)
- refund_netted: 10%
- duplicate_batch: 6%
- fee_misconfig: 8% (one order's fee 60% too high)
- orphan_credit: 7%
"""

from __future__ import annotations

import csv
import json
import random
from dataclasses import asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple

from app.schema import Order, SettlementLine, BankCredit, GLEntry, ExceptionReason

# Fixed seed for reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# Constants
RAZORPAY_FEE_RATE = 0.02       # 2%
GST_ON_FEE_RATE = 0.18         # 18% of fee
BATCH_SIZE = 6
NUM_ORDERS = 250               # Increased from 65 to 250 for medium-scale testing
BASE_ORDER_DATE = datetime(2026, 8, 1)
OUTPUT_DIR = Path(__file__).parent.parent / "data"

# Scenario weights (must sum to 100)
SCENARIOS = [
    ("clean", 45),
    ("partial_hold", 12),
    ("settlement_lag", 12),
    ("refund_netted", 10),
    ("duplicate_batch", 6),
    ("fee_misconfig", 8),
    ("orphan_credit", 7),
]


def weighted_choice() -> str:
    """Pick one scenario based on weights."""
    population = []
    for scenario, weight in SCENARIOS:
        population.extend([scenario] * weight)
    return random.choice(population)


def format_date(dt: datetime) -> str:
    """ISO-8601 date string."""
    return dt.strftime("%Y-%m-%d")


def generate_orders(num: int) -> List[Order]:
    """Generate synthetic orders with realistic amounts."""
    orders = []
    for i in range(1, num + 1):
        # Spread orders across a longer time period (30 days instead of 7)
        order_date = BASE_ORDER_DATE + timedelta(days=random.randint(0, 30))
        # More varied amounts: small (500-2K), medium (2K-10K), large (10K-50K)
        category = random.choices(
            ["small", "medium", "large", "xlarge"],
            weights=[40, 35, 20, 5],
            k=1
        )[0]
        
        if category == "small":
            gross_amount = round(random.uniform(500.0, 2000.0), 2)
        elif category == "medium":
            gross_amount = round(random.uniform(2000.0, 10000.0), 2)
        elif category == "large":
            gross_amount = round(random.uniform(10000.0, 25000.0), 2)
        else:  # xlarge
            gross_amount = round(random.uniform(25000.0, 50000.0), 2)
        
        orders.append(Order(
            order_id=f"ORD{i:05d}",  # 5 digits for larger dataset
            order_date=format_date(order_date),
            gross_amount=gross_amount,
            currency="INR",
            refunded_amount=0.0,
        ))
    return orders


def calculate_fees(gross: float) -> Tuple[float, float, float]:
    """
    Returns (razorpay_fee, gst_on_fee, net_amount).
    """
    fee = round(gross * RAZORPAY_FEE_RATE, 2)
    gst = round(fee * GST_ON_FEE_RATE, 2)
    net = round(gross - fee - gst, 2)
    return fee, gst, net


def generate_batches(orders: List[Order]) -> List[Dict]:
    """
    Group orders into batches of BATCH_SIZE.
    Each batch gets ONE scenario assigned.
    Returns list of batch dicts.
    """
    batches = []
    for batch_idx, i in enumerate(range(0, len(orders), BATCH_SIZE), start=1):
        batch_orders = orders[i:i + BATCH_SIZE]
        scenario = weighted_choice()
        # Settlement date varies: some T+0 (same day), most T+1, some T+2
        settlement_offset = random.choices([0, 1, 2], weights=[10, 70, 20], k=1)[0]
        # Use the earliest order date in batch as base
        min_order_date = min(datetime.fromisoformat(o.order_date) for o in batch_orders)
        batches.append({
            "batch_id": f"BATCH{batch_idx:04d}",  # 4 digits for larger dataset
            "orders": batch_orders,
            "scenario": scenario,
            "settlement_date": min_order_date + timedelta(days=settlement_offset),
        })
    return batches


def apply_scenario_logic(
    batch: Dict,
    settlements: List[SettlementLine],
    bank_credits: List[BankCredit],
    gl_entries: List[GLEntry],
    ground_truth: Dict[str, Dict],
) -> None:
    """
    Apply the scenario to the batch, mutating settlements/bank_credits/gl_entries in place.
    Also record ground_truth metadata.
    """
    scenario = batch["scenario"]
    batch_orders = batch["orders"]
    batch_id = batch["batch_id"]
    settlement_date = batch["settlement_date"]
    
    # Generate settlement lines for all orders in batch
    batch_gross = 0.0
    batch_net = 0.0
    
    # Pick one order to have fee_misconfig (if applicable)
    fee_misconfig_order = random.choice(batch_orders) if scenario == "fee_misconfig" else None
    
    for order in batch_orders:
        fee, gst, net = calculate_fees(order.gross_amount)
        
        # Inject fee_misconfig on ONE random order in the batch
        if scenario == "fee_misconfig" and order == fee_misconfig_order:
            fee = round(fee * 1.60, 2)  # 60% too high
            gst = round(fee * GST_ON_FEE_RATE, 2)
            net = round(order.gross_amount - fee - gst, 2)
            ground_truth[order.order_id] = {
                "scenario": "fee_misconfig_order",  # Mark specifically as the fee-inflated order
                "expected_exception_reason": ExceptionReason.fee_mismatch.value,
            }
        else:
            # All other orders in any batch
            # - fee_misconfig: non-modified orders are actually clean (no exception)
            # - refund_netted/duplicate/etc: batch-level scenarios affect all orders
            ground_truth[order.order_id] = {
                "scenario": scenario,
                "expected_exception_reason": None if scenario == "fee_misconfig" else ("batch_level" if scenario != "clean" else None),
            }
        
        settlements.append(SettlementLine(
            settlement_id=f"SETT-{batch_id}-{order.order_id}",
            order_id=order.order_id,
            settled_date=format_date(settlement_date),
            gross_amount=order.gross_amount,
            razorpay_fee=fee,
            gst_on_fee=gst,
            net_amount=net,
            is_partial_hold=(scenario == "partial_hold"),
            hold_reason="Risk Review" if scenario == "partial_hold" else None,
        ))
        
        batch_gross += order.gross_amount
        batch_net += net
    
    # Handle batch-level scenarios
    utr = f"UTR{random.randint(100000000, 999999999)}"
    bank_date = settlement_date + timedelta(days=1)  # T+1 default
    
    if scenario == "partial_hold":
        # Withhold 5% of batch_net
        withheld = round(batch_net * 0.05, 2)
        actual_credit = round(batch_net - withheld, 2)
        bank_credits.append(BankCredit(
            credit_id=f"BC-{batch_id}",
            value_date=format_date(bank_date),
            utr=utr,
            amount=actual_credit,
            raw_narration=f"RAZORPAY SETT {batch_id} PARTIAL",
        ))
    
    elif scenario == "settlement_lag":
        # Bank credit arrives T+3 to T+7 instead of T+1/T+2
        lag_days = random.randint(3, 7)
        bank_date = settlement_date + timedelta(days=lag_days)
        bank_credits.append(BankCredit(
            credit_id=f"BC-{batch_id}",
            value_date=format_date(bank_date),
            utr=utr,
            amount=batch_net,
            raw_narration=f"RAZORPAY SETTLEMENT {batch_id} DELAYED",
        ))
    
    elif scenario == "refund_netted":
        # Subtract a refund from batch net (10-30% of batch)
        refund_pct = random.uniform(0.10, 0.30)
        refund_amount = round(batch_net * refund_pct, 2)
        actual_credit = round(batch_net - refund_amount, 2)
        bank_credits.append(BankCredit(
            credit_id=f"BC-{batch_id}",
            value_date=format_date(bank_date),
            utr=utr,
            amount=actual_credit,
            raw_narration=f"RAZORPAY SETT {batch_id} NET OF REFUND",
        ))
    
    elif scenario == "duplicate_batch":
        # Same UTR appears twice
        bank_credits.append(BankCredit(
            credit_id=f"BC-{batch_id}-A",
            value_date=format_date(bank_date),
            utr=utr,
            amount=batch_net,
            raw_narration=f"RAZORPAY SETTLEMENT {batch_id}",
        ))
        bank_credits.append(BankCredit(
            credit_id=f"BC-{batch_id}-B",
            value_date=format_date(bank_date),
            utr=utr,  # SAME UTR
            amount=batch_net,
            raw_narration=f"RAZORPAY SETTLEMENT {batch_id} DUPLICATE",
        ))
    
    elif scenario == "orphan_credit":
        # Normal batch credit + one orphan
        bank_credits.append(BankCredit(
            credit_id=f"BC-{batch_id}",
            value_date=format_date(bank_date),
            utr=utr,
            amount=batch_net,
            raw_narration=f"RAZORPAY SETTLEMENT {batch_id}",
        ))
        # Orphan credit with no reference
        orphan_utr = f"UTR{random.randint(100000000, 999999999)}"
        orphan_amount = round(random.uniform(1000.0, 5000.0), 2)
        bank_credits.append(BankCredit(
            credit_id=f"BC-ORPHAN-{batch_id}",
            value_date=format_date(bank_date + timedelta(days=1)),
            utr=orphan_utr,
            amount=orphan_amount,
            raw_narration="UNKNOWN CREDIT",
        ))
    
    else:  # clean
        bank_credits.append(BankCredit(
            credit_id=f"BC-{batch_id}",
            value_date=format_date(bank_date),
            utr=utr,
            amount=batch_net,
            raw_narration=f"RAZORPAY SETTLEMENT {batch_id}",
        ))
    
    # Generate GL entries with realistic formatting drift
    gl_id_base = f"GL-{batch_id}"
    gl_date = format_date(settlement_date)
    
    # Sales Revenue - various formats
    sales_formats = [
        "Sales Revenue", "Sales : Online", "SALES-ONLINE", 
        "Online Sales:Retail", "Revenue - Sales", "Sales/Online"
    ]
    gl_entries.append(GLEntry(
        gl_id=f"{gl_id_base}-SR",
        entry_date=gl_date,
        account=random.choice(sales_formats),
        amount_str=format_dirty_amount(batch_gross),
        reference=batch_id,
    ))
    
    # Razorpay Fees
    fee_total = sum(s.razorpay_fee for s in settlements if s.settlement_id.startswith(f"SETT-{batch_id}"))
    fee_formats = ["Razorpay Fees", "Payment Gateway Fee", "RAZORPAY-FEE", "Fees:Razorpay"]
    gl_entries.append(GLEntry(
        gl_id=f"{gl_id_base}-FEE",
        entry_date=gl_date,
        account=random.choice(fee_formats),
        amount_str=format_dirty_amount(-fee_total),  # negative expense
        reference=batch_id,
    ))
    
    # GST on Fees
    gst_total = sum(s.gst_on_fee for s in settlements if s.settlement_id.startswith(f"SETT-{batch_id}"))
    gst_formats = ["GST on Fees (Input Credit)", "GST-INPUT", "GST : Fees", "Input GST/Fees"]
    gl_entries.append(GLEntry(
        gl_id=f"{gl_id_base}-GST",
        entry_date=gl_date,
        account=random.choice(gst_formats),
        amount_str=format_dirty_amount(-gst_total),
        reference=batch_id,
    ))


def format_dirty_amount(amount: float) -> str:
    """Format money with realistic variations: ₹ symbols, commas, inconsistent spacing."""
    formats = [
        f"₹{amount:,.2f}",
        f"₹ {amount:,.2f}",
        f"{amount:,.2f}",
        f"INR {amount:,.2f}",
        f"{amount:.2f}",  # no commas
    ]
    return random.choice(formats)


def write_csv(filename: str, rows: List[Dict], fieldnames: List[str]) -> None:
    """Write a list of dicts to CSV."""
    filepath = OUTPUT_DIR / filename
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"✓ Wrote {len(rows)} rows to {filepath}")


def main():
    """Generate all synthetic data."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating {NUM_ORDERS} orders in batches of {BATCH_SIZE}...")
    
    # 1. Generate orders
    orders = generate_orders(NUM_ORDERS)
    
    # 2. Group into batches with scenarios
    batches = generate_batches(orders)
    
    # 3. Generate settlements, bank credits, GL entries
    settlements: List[SettlementLine] = []
    bank_credits: List[BankCredit] = []
    gl_entries: List[GLEntry] = []
    ground_truth: Dict[str, Dict] = {}
    
    for batch in batches:
        apply_scenario_logic(batch, settlements, bank_credits, gl_entries, ground_truth)
    
    # 4. Write CSVs
    write_csv(
        "orders_ledger.csv",
        [asdict(o) for o in orders],
        ["order_id", "order_date", "gross_amount", "currency", "refunded_amount"],
    )
    
    write_csv(
        "razorpay_settlements.csv",
        [asdict(s) for s in settlements],
        ["settlement_id", "order_id", "settled_date", "gross_amount", 
         "razorpay_fee", "gst_on_fee", "net_amount", "is_partial_hold", "hold_reason"],
    )
    
    write_csv(
        "bank_statement.csv",
        [asdict(b) for b in bank_credits],
        ["credit_id", "value_date", "utr", "amount", "raw_narration"],
    )
    
    write_csv(
        "gl_export.csv",
        [asdict(g) for g in gl_entries],
        ["gl_id", "entry_date", "account", "amount_str", "reference"],
    )
    
    # 5. Write ground truth JSON
    gt_path = OUTPUT_DIR / "ground_truth.json"
    with open(gt_path, "w", encoding="utf-8") as f:
        json.dump(ground_truth, f, indent=2)
    print(f"✓ Wrote ground truth to {gt_path}")
    
    # Summary
    scenario_counts = {}
    for batch in batches:
        sc = batch["scenario"]
        scenario_counts[sc] = scenario_counts.get(sc, 0) + 1
    
    print("\n=== Scenario Distribution ===")
    for scenario, count in sorted(scenario_counts.items()):
        print(f"  {scenario:20s} : {count:2d} batches")
    
    print(f"\n✓ All data generated in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
