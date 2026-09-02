"""Debug categorize.py topic identification."""

from pathlib import Path
from app.reconcile import load_orders, load_settlements, load_bank_credits, run_reconciliation
from app.categorize import _identify_kb_topic
import json

DATA_DIR = Path(__file__).parent.parent / "data"

# Load ground truth
with open(DATA_DIR / "ground_truth.json", "r") as f:
    ground_truth = json.load(f)

# Load reconciliation
orders = load_orders(DATA_DIR / "orders_ledger.csv")
settlements = load_settlements(DATA_DIR / "razorpay_settlements.csv")
bank_credits = load_bank_credits(DATA_DIR / "bank_statement.csv")

results = run_reconciliation(orders, settlements, bank_credits)

# Find refund_not_netted results
refund_results = [r for r in results if r.exception_reason and r.exception_reason.value == "refund_not_netted"]

print("=" * 100)
print("ANALYZING REFUND_NOT_NETTED CASES — WHERE DO THEY ROUTE?")
print("=" * 100)

for result in refund_results[:3]:
    audit_text = " ".join(result.audit_trail)
    identified_topic = _identify_kb_topic(audit_text, result.status.value)
    
    print(f"\n{result.order_id}:")
    print(f"  Status: {result.status.value}")
    print(f"  Exception reason (from recon): {result.exception_reason.value if result.exception_reason else None}")
    print(f"  Identified KB topic: {identified_topic}")
    print(f"  Audit trail snippet: {result.audit_trail[-1] if result.audit_trail else 'N/A'}")
    print(f"  Full audit:")
    for line in result.audit_trail:
        print(f"    {line}")

print("\n" + "=" * 100)
print("KEYWORD MATCHING ANALYSIS")
print("=" * 100)

if refund_results:
    result = refund_results[0]
    audit_text = " ".join(result.audit_trail).lower()
    
    # Check what keywords match
    keywords_to_check = {
        'settlement_lag': ['days after settlement', 'delayed', 't+3', 't+4', 't+5', 't+6', 't+7'],
        'duplicate_batch': ['duplicate', 'same utr', 'multiple credits', 'overlapping utrs'],
        'partial_hold': ['partial_hold', 'withheld', 'reserve'],
        'fee_mismatch': ['fee mismatch', 'fee variance', 'deviat', 'threshold'],
        'refund_not_netted': ['shortage', 'short by', 'unexplained', 'refund'],
    }
    
    print(f"Audit text (lowercase): {audit_text}")
    print()
    
    for topic, keywords in keywords_to_check.items():
        matches = [kw for kw in keywords if kw in audit_text]
        if matches:
            print(f"  {topic}: {matches}")
        else:
            print(f"  {topic}: NO MATCH")
