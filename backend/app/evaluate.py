"""
evaluate.py — comprehensive evaluation against ground truth for SettleTrace.

Scores the reconciliation engine + categorization agent against known scenarios
with honest metrics including confidence-routed coverage and unresolved cases.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Any, Tuple

from app.reconcile import load_orders, load_settlements, load_bank_credits, run_reconciliation
from app.categorize import explain_exception
from app.schema import MatchStatus


DATA_DIR = Path(__file__).parent.parent / "data"


def load_ground_truth(filepath: Path) -> Dict[str, Dict[str, Any]]:
    """Load ground truth mapping from JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def convert_results_to_dicts(results: List[Any]) -> List[Dict[str, Any]]:
    """Convert ReconciliationResult dataclass objects to dicts for categorize module."""
    result_dicts = []
    for r in results:
        result_dict = {
            "order_id": r.order_id,
            "status": r.status.value,
            "matched_settlement_id": r.matched_settlement_id,
            "matched_bank_credit_id": r.matched_bank_credit_id,
            "expected_net": r.expected_net,
            "actual_net": r.actual_net,
            "delta": r.delta,
            "exception_reason": r.exception_reason.value if r.exception_reason else None,
            "llm_explanation": r.llm_explanation,
            "cited_rule": r.cited_rule,
            "confidence": r.confidence,
            "audit_trail": r.audit_trail[:],  # Copy list
        }
        result_dicts.append(result_dict)
    return result_dicts


def run_full_pipeline() -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    """
    Run the full reconciliation + categorization pipeline.
    
    Returns
    -------
    tuple
        (final_results, ground_truth) where final_results includes LLM explanations
        for orders that needed agent review.
    """
    print("Loading data...")
    orders = load_orders(DATA_DIR / "orders_ledger.csv")
    settlements = load_settlements(DATA_DIR / "razorpay_settlements.csv")
    bank_credits = load_bank_credits(DATA_DIR / "bank_statement.csv")
    ground_truth = load_ground_truth(DATA_DIR / "ground_truth.json")
    
    print("Running reconciliation engine...")
    reconcile_results = run_reconciliation(orders, settlements, bank_credits)
    
    # Convert to dicts
    result_dicts = convert_results_to_dicts(reconcile_results)
    
    # Filter order-level results (exclude orphan pseudo-results)
    order_results = [r for r in result_dicts if not r["order_id"].startswith("ORPHAN-")]
    
    print("Identifying results needing agent review...")
    # These are the ones that need LLM categorization
    needs_agent = []
    deterministic = []
    
    for result in order_results:
        status = result["status"]
        if status in ["matched", "settlement_lag", "partial_hold"]:
            # Deterministically resolved by reconcile engine
            deterministic.append(result)
        else:
            # Needs agent: needs_review, unresolved, etc.
            needs_agent.append(result)
    
    print(f"  Deterministic results: {len(deterministic)}")
    print(f"  Needs agent review: {len(needs_agent)}")
    
    print("Running categorization agent...")
    if needs_agent:
        categorized = []
        for result in needs_agent:
            explained = explain_exception(result)
            categorized.append(explained)
        
        # Combine deterministic + agent results
        final_results = deterministic + categorized
    else:
        final_results = deterministic
    
    return final_results, ground_truth


def calculate_reconciliation_match_rate(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate overall reconciliation success metrics."""
    total_orders = len(results)
    
    # Count by status
    status_counts = defaultdict(int)
    for r in results:
        status_counts[r["status"]] += 1
    
    # Resolved = matched + deterministically explained
    resolved_statuses = ["matched", "settlement_lag", "partial_hold"]
    resolved_count = sum(status_counts[status] for status in resolved_statuses)
    
    match_rate = (resolved_count / total_orders * 100) if total_orders > 0 else 0
    
    return {
        "total_orders": total_orders,
        "resolved_count": resolved_count,
        "match_rate_percent": round(match_rate, 2),
        "status_breakdown": dict(status_counts),
    }


def calculate_classification_accuracy(
    results: List[Dict[str, Any]], 
    ground_truth: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate precision/recall for exception classification on agent-reviewed cases.
    """
    # Filter to cases that went through the agent
    agent_cases = [r for r in results if r["status"] not in ["matched", "settlement_lag", "partial_hold"]]
    
    if not agent_cases:
        return {
            "total_agent_cases": 0,
            "overall_accuracy": 0.0,
            "per_reason_metrics": {},
            "confusion_matrix": {},
        }
    
    # Build confusion matrix: predicted_reason -> actual_reason -> count
    confusion = defaultdict(lambda: defaultdict(int))
    correct_predictions = 0
    
    predicted_reasons = defaultdict(int)  # reason -> count
    actual_reasons = defaultdict(int)     # reason -> count
    
    for result in agent_cases:
        order_id = result["order_id"]
        predicted_reason = result.get("exception_reason", "unknown")
        
        # Get ground truth expected reason
        gt_entry = ground_truth.get(order_id, {})
        actual_reason = gt_entry.get("expected_exception_reason")
        
        # Handle "batch_level" ground truth (means scenario affects whole batch)
        if actual_reason == "batch_level":
            # Map from scenario to expected reason
            scenario = gt_entry.get("scenario", "")
            actual_reason = _scenario_to_reason(scenario)
        
        # Handle None/null cases
        if actual_reason is None:
            actual_reason = "unknown"
        
        # Count
        predicted_reasons[predicted_reason] += 1
        actual_reasons[actual_reason] += 1
        confusion[predicted_reason][actual_reason] += 1
        
        if predicted_reason == actual_reason:
            correct_predictions += 1
    
    # Calculate per-reason precision/recall
    per_reason_metrics = {}
    all_reasons = set(predicted_reasons.keys()) | set(actual_reasons.keys())
    
    for reason in all_reasons:
        # Precision = TP / (TP + FP) = correct_predictions_for_reason / total_predictions_for_reason
        tp = confusion[reason][reason]
        fp = sum(confusion[reason][other] for other in confusion[reason] if other != reason)
        fn = sum(confusion[other][reason] for other in confusion if other != reason)
        
        precision = (tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        recall = (tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
        
        per_reason_metrics[reason] = {
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1_score": round(f1, 3),
            "support": actual_reasons[reason],
        }
    
    # Overall accuracy
    overall_accuracy = (correct_predictions / len(agent_cases)) if agent_cases else 0.0
    
    return {
        "total_agent_cases": len(agent_cases),
        "overall_accuracy": round(overall_accuracy, 3),
        "per_reason_metrics": per_reason_metrics,
        "confusion_matrix": {pred: dict(actual_dict) for pred, actual_dict in confusion.items()},
    }


def _scenario_to_reason(scenario: str) -> str:
    """Map ground truth scenario to expected exception_reason."""
    mapping = {
        "refund_netted": "refund_not_netted",
        "duplicate_batch": "duplicate_batch", 
        "fee_misconfig": "fee_mismatch",
        "orphan_credit": "orphan_bank_credit",
        "settlement_lag": "settlement_lag",  # shouldn't reach agent, but just in case
        "partial_hold": "partial_hold",      # shouldn't reach agent, but just in case
        "clean": None,                       # shouldn't have exceptions
    }
    return mapping.get(scenario, "unknown")


def calculate_confidence_coverage(results: List[Dict[str, Any]], ground_truth: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate accuracy at different confidence thresholds (honesty metrics)."""
    # Filter to agent cases
    agent_cases = [r for r in results if r["status"] not in ["matched", "settlement_lag", "partial_hold"]]
    
    if not agent_cases:
        return {
            "high_confidence_threshold": 0.7,
            "high_confidence_count": 0,
            "high_confidence_accuracy": 0.0,
            "all_confidence_count": 0,
            "all_confidence_accuracy": 0.0,
        }
    
    # Score all cases
    all_correct = 0
    high_conf_cases = []
    high_conf_correct = 0
    
    for result in agent_cases:
        order_id = result["order_id"]
        predicted_reason = result.get("exception_reason", "unknown")
        confidence = result.get("confidence", 0.0)
        
        # Get actual reason
        gt_entry = ground_truth.get(order_id, {})
        actual_reason = gt_entry.get("expected_exception_reason")
        if actual_reason == "batch_level":
            scenario = gt_entry.get("scenario", "")
            actual_reason = _scenario_to_reason(scenario)
        if actual_reason is None:
            actual_reason = "unknown"
        
        # Check correctness
        is_correct = (predicted_reason == actual_reason)
        if is_correct:
            all_correct += 1
        
        # High confidence cases
        if confidence >= 0.7:
            high_conf_cases.append(result)
            if is_correct:
                high_conf_correct += 1
    
    return {
        "high_confidence_threshold": 0.7,
        "high_confidence_count": len(high_conf_cases),
        "high_confidence_accuracy": round((high_conf_correct / len(high_conf_cases)), 3) if high_conf_cases else 0.0,
        "all_confidence_count": len(agent_cases),
        "all_confidence_accuracy": round((all_correct / len(agent_cases)), 3) if agent_cases else 0.0,
    }


def find_unresolved_cases(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Find orders still needing manual review (status=unresolved or low confidence)."""
    unresolved = []
    
    for result in results:
        status = result["status"]
        confidence = result.get("confidence", 1.0)
        
        # Unresolved status OR low confidence from agent
        if status == "unresolved" or (status not in ["matched", "settlement_lag", "partial_hold"] and confidence < 0.5):
            unresolved.append(result)
    
    return unresolved


def print_evaluation_report(metrics: Dict[str, Any]) -> None:
    """Print a clean summary report."""
    print()
    print("=" * 80)
    print("SETTLETRACE EVALUATION REPORT")
    print("=" * 80)
    
    # 1. Reconciliation match rate
    recon = metrics["reconciliation_metrics"]
    print(f"\n📊 RECONCILIATION PERFORMANCE")
    print(f"   Total orders processed    : {recon['total_orders']}")
    print(f"   Deterministically resolved: {recon['resolved_count']} ({recon['match_rate_percent']}%)")
    print(f"   Status breakdown:")
    for status, count in sorted(recon["status_breakdown"].items()):
        pct = (count / recon["total_orders"] * 100)
        print(f"     {status:20s}: {count:3d} ({pct:5.1f}%)")
    
    # 2. Classification accuracy
    classif = metrics["classification_metrics"]
    print(f"\n🎯 AGENT CLASSIFICATION ACCURACY")
    print(f"   Cases requiring agent     : {classif['total_agent_cases']}")
    print(f"   Overall accuracy          : {classif['overall_accuracy']:.1%}")
    
    if classif["per_reason_metrics"]:
        print(f"   Per-reason metrics:")
        print(f"     {'Reason':<20} {'Precision':>9} {'Recall':>7} {'F1':>6} {'Support':>7}")
        print(f"     {'-'*20} {'-'*9} {'-'*7} {'-'*6} {'-'*7}")
        for reason, m in sorted(classif["per_reason_metrics"].items()):
            print(f"     {reason:<20} {m['precision']:>9.3f} {m['recall']:>7.3f} {m['f1_score']:>6.3f} {m['support']:>7d}")
    
    # 3. Confidence coverage
    conf = metrics["confidence_metrics"]
    print(f"\n🔍 CONFIDENCE-ROUTED COVERAGE")
    print(f"   High confidence (≥0.7)    : {conf['high_confidence_count']} cases, {conf['high_confidence_accuracy']:.1%} accuracy")
    print(f"   All confidence levels     : {conf['all_confidence_count']} cases, {conf['all_confidence_accuracy']:.1%} accuracy")
    if conf["high_confidence_count"] > 0:
        precision_gain = conf["high_confidence_accuracy"] - conf["all_confidence_accuracy"]
        print(f"   Precision gain at ≥0.7    : {precision_gain:+.1%}")
    
    # 4. Unresolved cases
    unresolved = metrics["unresolved_cases"]
    print(f"\n⚠️  CASES REQUIRING MANUAL REVIEW")
    print(f"   Count: {len(unresolved)}")
    if unresolved:
        print(f"   Details:")
        for case in unresolved:
            order_id = case["order_id"]
            status = case["status"]
            conf = case.get("confidence", 1.0)
            reason = case.get("exception_reason", "none")
            print(f"     {order_id}: status={status}, reason={reason}, confidence={conf:.2f}")
    
    print("\n" + "=" * 80)


def write_metrics_json(metrics: Dict[str, Any], filepath: Path) -> None:
    """Write metrics to JSON file for FastAPI serving."""
    # Prepare JSON-serializable version
    json_metrics = {
        "timestamp": "2026-09-02T12:00:00Z",  # Would be datetime.now().isoformat() in real use
        "reconciliation_metrics": metrics["reconciliation_metrics"],
        "classification_metrics": metrics["classification_metrics"],
        "confidence_metrics": metrics["confidence_metrics"],
        "unresolved_cases_count": len(metrics["unresolved_cases"]),
        "unresolved_cases": [
            {
                "order_id": case["order_id"],
                "status": case["status"],
                "exception_reason": case.get("exception_reason"),
                "confidence": case.get("confidence", 1.0),
                "expected_net": case.get("expected_net", 0.0),
                "actual_net": case.get("actual_net", 0.0),
                "delta": case.get("delta", 0.0),
            }
            for case in metrics["unresolved_cases"]
        ],
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(json_metrics, f, indent=2)
    
    print(f"\n📄 Metrics written to {filepath}")


def main() -> Dict[str, Any]:
    """Run full evaluation pipeline."""
    print("=" * 80)
    print("RUNNING SETTLETRACE EVALUATION")
    print("=" * 80)
    
    # Run pipeline
    final_results, ground_truth = run_full_pipeline()
    
    print("Calculating metrics...")
    
    # Calculate all metrics
    reconciliation_metrics = calculate_reconciliation_match_rate(final_results)
    classification_metrics = calculate_classification_accuracy(final_results, ground_truth)
    confidence_metrics = calculate_confidence_coverage(final_results, ground_truth)
    unresolved_cases = find_unresolved_cases(final_results)
    
    metrics = {
        "reconciliation_metrics": reconciliation_metrics,
        "classification_metrics": classification_metrics,
        "confidence_metrics": confidence_metrics,
        "unresolved_cases": unresolved_cases,
    }
    
    # Print report
    print_evaluation_report(metrics)
    
    # Write JSON
    write_metrics_json(metrics, DATA_DIR / "metrics.json")
    
    return metrics


if __name__ == "__main__":
    main()