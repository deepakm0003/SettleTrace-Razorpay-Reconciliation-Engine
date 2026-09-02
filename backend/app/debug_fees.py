"""Debug fee checking logic."""

from pathlib import Path
from app.reconcile import load_orders, load_settlements, load_bank_credits, check_fee_accuracy, RAZORPAY_FEE_RATE
import json

DATA_DIR = Path(__file__).parent.parent / "data"

# Load data
orders = load_orders(DATA_DIR / "orders_ledger.csv")
settlements = load_settlements(DATA_DIR / "razorpay_settlements.csv")

with open(DATA_DIR / "ground_truth.json", "r") as f:
    ground_truth = json.load(f)

# Find fee_misconfig orders
fee_misconfig_orders = {
    oid for oid, meta in ground_truth.items()
    if meta.get("scenario") == "fee_misconfig"
}

print("ANALYZING FEE_MISCONFIG ORDERS")
print("=" * 100)

order_map = {o.order_id: o for o in orders}
settlement_map = {s.order_id: s for s in settlements}

for oid in sorted(fee_misconfig_orders)[:3]:
    order = order_map.get(oid)
    settlement = settlement_map.get(oid)
    
    if not order or not settlement:
        print(f"\n{oid}: missing order or settlement")
        continue
    
    expected_fee = round(order.gross_amount * RAZORPAY_FEE_RATE, 2)
    actual_fee = settlement.razorpay_fee
    
    is_accurate, variance = check_fee_accuracy(order.gross_amount, actual_fee)
    
    print(f"\n{oid}:")
    print(f"  Order gross: ₹{order.gross_amount:.2f}")
    print(f"  Expected fee (2%): ₹{expected_fee:.2f}")
    print(f"  Actual fee: ₹{actual_fee:.2f}")
    print(f"  Variance: {variance:.1%}")
    print(f"  Is accurate (≤15% variance): {is_accurate}")
    print(f"  Settlement net: ₹{settlement.net_amount:.2f}")

print("\n" + "=" * 100)
print("CHECKING THRESHOLD")
print(f"Threshold for fee accuracy: 15% variance")
print(f"fee_misconfig scenario injects: 60% higher fees (fee * 1.60)")
print(f"Expected variance: ~60%, which exceeds 15% threshold")
print(f"\nConclusion: Fee check SHOULD flag these as inaccurate.")
print(f"If they're not being flagged, there's a logic error in reconcile.py check_fee_accuracy().")
