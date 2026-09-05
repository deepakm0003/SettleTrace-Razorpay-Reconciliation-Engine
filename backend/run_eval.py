"""
run_eval.py — one-shot: reconcile + classify (5 workers) + write metrics.json
Run from backend/: python run_eval.py
"""
import json, time, threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from app.reconcile import load_orders, load_settlements, load_bank_credits, run_reconciliation
from app.categorize import explain_exception
from app.evaluate import (
    convert_results_to_dicts,
    calculate_reconciliation_match_rate,
    calculate_classification_accuracy,
    calculate_confidence_coverage,
    find_unresolved_cases,
    write_metrics_json,
    load_ground_truth,
)

DATA_DIR = Path("data")

# ── 1. Load & reconcile ────────────────────────────────────────────────────
print("Loading data...")
orders       = load_orders(DATA_DIR / "orders_ledger.csv")
settlements  = load_settlements(DATA_DIR / "razorpay_settlements.csv")
bank         = load_bank_credits(DATA_DIR / "bank_statement.csv")
ground_truth = load_ground_truth(DATA_DIR / "ground_truth.json")

print("Running reconciliation engine...")
results = run_reconciliation(orders, settlements, bank)
dicts   = convert_results_to_dicts(results)
orders_only = [r for r in dicts if not r["order_id"].startswith("ORPHAN-")]

det   = [r for r in orders_only if r["status"] in ("matched", "settlement_lag", "partial_hold")]
agent = [r for r in orders_only if r["status"] not in ("matched", "settlement_lag", "partial_hold")]

# Only classify first 50 via API — rest get mock fallback
API_SAMPLE  = 50
agent_api   = agent[:API_SAMPLE]
agent_mock  = agent[API_SAMPLE:]
print(f"  Deterministic: {len(det)}  |  Agent total: {len(agent)}  |  API sample: {len(agent_api)}  |  Mock rest: {len(agent_mock)}")

# ── 2. Classify with 5 parallel workers ───────────────────────────────────
print(f"Classifying {len(agent_api)} cases via NVIDIA NIM (5 workers)...")
t0          = time.time()
done        = [0]
lock        = threading.Lock()
categorized_api = [None] * len(agent_api)

def classify_one(args):
    idx, result = args
    out = explain_exception(result)
    with lock:
        done[0] += 1
        print(f"  [{done[0]}/{len(agent_api)}] {result['order_id']} done")
    return idx, out

with ThreadPoolExecutor(max_workers=5) as pool:
    for idx, out in pool.map(classify_one, enumerate(agent_api)):
        categorized_api[idx] = out

print(f"API classification done in {time.time() - t0:.0f}s")

# Classify remaining 400 with fast offline mock
print(f"Classifying remaining {len(agent_mock)} cases with offline mock...")
from app.model import _mock_llm
categorized_mock = []
for r in agent_mock:
    mock_result = json.loads(_mock_llm(
        " ".join(r.get("audit_trail", [])) + " " + str(r.get("delta", ""))
    ))
    r_copy = dict(r)
    r_copy["exception_reason"] = mock_result["reason"]
    r_copy["confidence"]       = mock_result["confidence"]
    r_copy["llm_explanation"]  = mock_result["explanation"]
    r_copy["cited_rule"]       = r_copy.get("cited_rule", "")
    categorized_mock.append(r_copy)

final = det + categorized_api + categorized_mock
print("Calculating metrics...")

rec  = calculate_reconciliation_match_rate(final)
cls  = calculate_classification_accuracy(final, ground_truth)
conf = calculate_confidence_coverage(final, ground_truth)
unr  = find_unresolved_cases(final)

metrics = {
    "reconciliation_metrics": rec,
    "classification_metrics": cls,
    "confidence_metrics":     conf,
    "unresolved_cases":       unr,
}

# ── 4. Write metrics.json ──────────────────────────────────────────────────
write_metrics_json(metrics, DATA_DIR / "metrics.json")

# ── 5. Print summary ───────────────────────────────────────────────────────
print()
print("=" * 60)
print("RESULTS")
print("=" * 60)
print(f"Total orders    : {rec['total_orders']}")
print(f"Match rate      : {rec['match_rate_percent']}%")
print(f"Agent cases     : {cls['total_agent_cases']}")
print(f"Agent accuracy  : {cls['overall_accuracy'] * 100:.1f}%")
print()
print(f"{'Reason':<28} {'F1':>6}  {'Support':>7}")
print("-" * 45)
for reason, m in sorted(cls["per_reason_metrics"].items()):
    print(f"  {reason:<26} {m['f1_score']:>6.2f}  {m['support']:>7}")
print()
print(f"metrics.json written to {DATA_DIR / 'metrics.json'}")
