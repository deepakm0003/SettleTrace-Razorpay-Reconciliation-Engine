"""Debug script to trace fee_misconfig and orphan_credit orders."""

from pathlib import Path
from app.reconcile import load_orders, load_settlements, load_bank_credits, run_reconciliation
from app.schema import MatchStatus, ExceptionReason

DATA_DIR = Path(__file__).parent.parent / "data"

# Load ground truth
import json
gt_path = DATA_DIR / "ground_truth.json"
with open(gt_path, "r") as f:
    ground_truth = json.load(f)

# Find orders that should be fee_misconfig or orphan_credit
fee_misconfig_orders = [
    oid for oid, meta in ground_truth.items()
    if meta.get("scenario") == "fee_misconfig"
]
orphan_credit_orders = [
    oid for oid, meta in ground_truth.items()
    if meta.get("scenario") == "orphan_credit"
]

print(f"Ground truth: {len(fee_misconfig_orders)} fee_misconfig orders, {len(orphan_credit_orders)} orphan_credit orders")
print(f"Fee misconfig order IDs: {fee_misconfig_orders[:5]}")
print(f"Orphan credit order IDs: {orphan_credit_orders[:5]}")

# Run reconciliation
orders = load_orders(DATA_DIR / "orders_ledger.csv")
settlements = load_settlements(DATA_DIR / "razorpay_settlements.csv")
bank_credits = load_bank_credits(DATA_DIR / "bank_statement.csv")

results = run_reconciliation(orders, settlements, bank_credits)

# Find what happened to fee_misconfig and orphan_credit orders
print("\n" + "=" * 80)
print("FEE_MISCONFIG ORDERS — WHERE DID THEY GO?")
print("=" * 80)

for oid in fee_misconfig_orders[:5]:
    result = next((r for r in results if r.order_id == oid), None)
    if result:
        print(f"\n{oid}:")
        print(f"  Status: {result.status.value}")
        print(f"  Exception reason: {result.exception_reason.value if result.exception_reason else None}")
        print(f"  Expected net: {result.expected_net}")
        print(f"  Actual net: {result.actual_net}")
        print(f"  Delta: {result.delta}")
        print(f"  LLM Explanation: {result.llm_explanation}")
    else:
        print(f"\n{oid}: NOT FOUND in results")

print("\n" + "=" * 80)
print("ORPHAN_CREDIT ORDERS — WHERE DID THEY GO?")
print("=" * 80)

for oid in orphan_credit_orders[:5]:
    result = next((r for r in results if r.order_id == oid), None)
    if result:
        print(f"\n{oid}:")
        print(f"  Status: {result.status.value}")
        print(f"  Exception reason: {result.exception_reason.value if result.exception_reason else None}")
        print(f"  Expected net: {result.expected_net}")
        print(f"  Actual net: {result.actual_net}")
        print(f"  Delta: {result.delta}")
        print(f"  LLM Explanation: {result.llm_explanation}")
    else:
        print(f"\n{oid}: NOT FOUND in results")

# Summary
print("\n" + "=" * 80)
print("STATUS DISTRIBUTION")
print("=" * 80)
from collections import Counter
status_counts = Counter(r.status.value for r in results)
for status, count in sorted(status_counts.items()):
    print(f"  {status}: {count}")

reason_counts = Counter(r.exception_reason.value if r.exception_reason else "None" for r in results)
print("\nEXCEPTION REASON DISTRIBUTION")
for reason, count in sorted(reason_counts.items()):
    print(f"  {reason}: {count}")
