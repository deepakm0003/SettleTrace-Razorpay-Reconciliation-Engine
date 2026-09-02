"""Debug ground truth expectations."""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

with open(DATA_DIR / "ground_truth.json", "r") as f:
    gt = json.load(f)

# Check refund_netted orders
refund_orders = {oid: meta for oid, meta in gt.items() if meta.get("scenario") == "refund_netted"}

print("REFUND_NETTED SCENARIO ORDERS:")
for oid in sorted(list(refund_orders.keys())[:6]):
    meta = refund_orders[oid]
    print(f"  {oid}: scenario={meta.get('scenario')}, expected_reason={meta.get('expected_exception_reason')}")

print(f"\nTotal: {len(refund_orders)} orders in refund_netted batches")

# Check fee_misconfig
fee_orders = {oid: meta for oid, meta in gt.items() if meta.get("scenario") == "fee_misconfig"}
print("\nFEE_MISCONFIG ORDERS:")
for oid in sorted(list(fee_orders.keys())[:6]):
    meta = fee_orders[oid]
    print(f"  {oid}: scenario={meta.get('scenario')}, expected_reason={meta.get('expected_exception_reason')}")

print(f"\nTotal: {len(fee_orders)} orders")

# Check fee_misconfig_order
fee_mismatch_orders = {oid: meta for oid, meta in gt.items() if meta.get("scenario") == "fee_misconfig_order"}
print("\nFEE_MISCONFIG_ORDER ORDERS:")
for oid in sorted(list(fee_mismatch_orders.keys())[:6]):
    meta = fee_mismatch_orders[oid]
    print(f"  {oid}: scenario={meta.get('scenario')}, expected_reason={meta.get('expected_exception_reason')}")

print(f"\nTotal: {len(fee_mismatch_orders)} orders")
