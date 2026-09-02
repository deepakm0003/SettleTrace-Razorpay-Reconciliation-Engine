"""
test_reconcile.py — comprehensive tests for the reconciliation engine.

Uses generated synthetic data with known ground truth to verify:
- All orders are processed
- Clean orders match perfectly
- Scenarios are correctly detected
- No invalid results (e.g., negative expected_net)
"""

import json
import shutil
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

import pytest

from app.generate_data import main as generate_data
from app.reconcile import (
    load_orders,
    load_settlements,
    load_bank_credits,
    run_reconciliation,
)
from app.schema import MatchStatus, ReconciliationResult


@pytest.fixture(scope="module")
def test_data_dir():
    """Create a temporary directory with generated test data."""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Temporarily patch the OUTPUT_DIR in generate_data
    import app.generate_data as gen_module
    original_output_dir = gen_module.OUTPUT_DIR
    gen_module.OUTPUT_DIR = temp_dir
    
    try:
        # Generate synthetic data
        generate_data()
        yield temp_dir
    finally:
        # Restore original OUTPUT_DIR
        gen_module.OUTPUT_DIR = original_output_dir
        # Clean up temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="module")
def ground_truth(test_data_dir: Path) -> Dict:
    """Load ground truth mapping."""
    with open(test_data_dir / "ground_truth.json", "r") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def reconciliation_results(test_data_dir: Path) -> List[ReconciliationResult]:
    """Run reconciliation and return results."""
    orders = load_orders(test_data_dir / "orders_ledger.csv")
    settlements = load_settlements(test_data_dir / "razorpay_settlements.csv")
    bank_credits = load_bank_credits(test_data_dir / "bank_statement.csv")
    
    return run_reconciliation(orders, settlements, bank_credits)


class TestReconciliationCompleteness:
    """Test that all orders are processed."""
    
    def test_all_orders_have_results(self, test_data_dir: Path, reconciliation_results: List[ReconciliationResult]):
        """Every order_id from orders_ledger.csv should appear exactly once in results."""
        orders = load_orders(test_data_dir / "orders_ledger.csv")
        order_ids = {o.order_id for o in orders}
        
        # Filter out orphan pseudo-results
        result_order_ids = {r.order_id for r in reconciliation_results if not r.order_id.startswith("ORPHAN-")}
        
        # Check all orders are present
        missing = order_ids - result_order_ids
        assert not missing, f"Missing results for orders: {missing}"
        
        # Check no duplicates
        result_order_list = [r.order_id for r in reconciliation_results if not r.order_id.startswith("ORPHAN-")]
        assert len(result_order_list) == len(set(result_order_list)), "Duplicate order results found"
        
        # Check counts match
        assert len(order_ids) == len(result_order_ids), \
            f"Expected {len(order_ids)} results, got {len(result_order_ids)}"


class TestScenarioDetection:
    """Test that scenarios are correctly detected against ground truth."""
    
    def test_clean_orders_match(self, ground_truth: Dict, reconciliation_results: List[ReconciliationResult]):
        """All 'clean' scenario orders should have status='matched'."""
        clean_order_ids = [
            oid for oid, data in ground_truth.items()
            if data["scenario"] == "clean"
        ]
        
        result_map = {r.order_id: r for r in reconciliation_results}
        
        mismatches = []
        for oid in clean_order_ids:
            result = result_map.get(oid)
            if not result:
                mismatches.append(f"{oid}: no result found")
            elif result.status != MatchStatus.matched:
                mismatches.append(f"{oid}: expected 'matched', got '{result.status.value}'")
        
        assert not mismatches, f"Clean scenario mismatches:\n" + "\n".join(mismatches)
    
    def test_settlement_lag_detected(self, ground_truth: Dict, reconciliation_results: List[ReconciliationResult]):
        """All 'settlement_lag' scenario orders should have status='settlement_lag'."""
        lag_order_ids = [
            oid for oid, data in ground_truth.items()
            if data["scenario"] == "settlement_lag"
        ]
        
        result_map = {r.order_id: r for r in reconciliation_results}
        
        mismatches = []
        for oid in lag_order_ids:
            result = result_map.get(oid)
            if not result:
                mismatches.append(f"{oid}: no result found")
            elif result.status != MatchStatus.settlement_lag:
                mismatches.append(
                    f"{oid}: expected 'settlement_lag', got '{result.status.value}'"
                )
        
        assert not mismatches, f"Settlement lag mismatches:\n" + "\n".join(mismatches)
    
    def test_partial_hold_detected(self, ground_truth: Dict, reconciliation_results: List[ReconciliationResult]):
        """All 'partial_hold' scenario orders should have status='partial_hold'."""
        hold_order_ids = [
            oid for oid, data in ground_truth.items()
            if data["scenario"] == "partial_hold"
        ]
        
        if not hold_order_ids:
            pytest.skip("No partial_hold scenarios in this test run")
        
        result_map = {r.order_id: r for r in reconciliation_results}
        
        mismatches = []
        for oid in hold_order_ids:
            result = result_map.get(oid)
            if not result:
                mismatches.append(f"{oid}: no result found")
            elif result.status != MatchStatus.partial_hold:
                mismatches.append(
                    f"{oid}: expected 'partial_hold', got '{result.status.value}'"
                )
        
        assert not mismatches, f"Partial hold mismatches:\n" + "\n".join(mismatches)
    
    def test_refund_netted_flagged(self, ground_truth: Dict, reconciliation_results: List[ReconciliationResult]):
        """'refund_netted' scenario orders should not have status='matched'."""
        refund_order_ids = [
            oid for oid, data in ground_truth.items()
            if data["scenario"] == "refund_netted"
        ]
        
        if not refund_order_ids:
            pytest.skip("No refund_netted scenarios in this test run")
        
        result_map = {r.order_id: r for r in reconciliation_results}
        
        incorrectly_matched = []
        for oid in refund_order_ids:
            result = result_map.get(oid)
            if result and result.status == MatchStatus.matched:
                incorrectly_matched.append(oid)
        
        assert not incorrectly_matched, \
            f"Refund scenarios incorrectly marked as matched: {incorrectly_matched}"


class TestDataValidity:
    """Test that results are valid and internally consistent."""
    
    def test_no_negative_expected_net(self, reconciliation_results: List[ReconciliationResult]):
        """No result should have a negative expected_net."""
        negative_results = [
            r for r in reconciliation_results
            if r.expected_net < 0 and not r.order_id.startswith("ORPHAN-")
        ]
        
        assert not negative_results, \
            f"Found {len(negative_results)} results with negative expected_net: " \
            f"{[(r.order_id, r.expected_net) for r in negative_results]}"
    
    def test_all_results_have_audit_trail(self, reconciliation_results: List[ReconciliationResult]):
        """Every result should have a non-empty audit trail."""
        missing_trail = [r.order_id for r in reconciliation_results if not r.audit_trail]
        
        assert not missing_trail, f"Results missing audit trail: {missing_trail}"
    
    def test_matched_results_have_reasonable_delta(self, reconciliation_results: List[ReconciliationResult]):
        """Results with status='matched' should have reasonable delta (batch-level matching)."""
        # Note: Delta is calculated as (actual_batch_net / batch_size) - expected_order_net
        # For matched batches, this can be non-zero per order due to pro-rata division,
        # but the sum across all orders in a batch should be near zero.
        
        # Group matched results by batch
        from collections import defaultdict
        batch_deltas = defaultdict(float)
        
        for r in reconciliation_results:
            if r.status == MatchStatus.matched and r.matched_settlement_id:
                # Extract batch ID from settlement ID
                parts = r.matched_settlement_id.split("-")
                if len(parts) >= 2:
                    batch_id = parts[1]
                    batch_deltas[batch_id] += r.delta
        
        # Check that each batch's total delta is near zero
        BATCH_TOLERANCE = 0.10  # 10 paisa total per batch
        high_batch_deltas = [
            (batch_id, delta) for batch_id, delta in batch_deltas.items()
            if abs(delta) > BATCH_TOLERANCE
        ]
        
        assert not high_batch_deltas, \
            f"Matched batches with high total delta: {high_batch_deltas}"


class TestMatchRate:
    """Test overall match rate on clean scenarios."""
    
    def test_clean_scenario_match_rate_100_percent(
        self, 
        ground_truth: Dict, 
        reconciliation_results: List[ReconciliationResult]
    ):
        """Match rate on 'clean' scenario orders should be 100%."""
        clean_order_ids = [
            oid for oid, data in ground_truth.items()
            if data["scenario"] == "clean"
        ]
        
        result_map = {r.order_id: r for r in reconciliation_results}
        
        matched_count = sum(
            1 for oid in clean_order_ids
            if result_map.get(oid) and result_map[oid].status == MatchStatus.matched
        )
        
        total_clean = len(clean_order_ids)
        match_rate = (matched_count / total_clean * 100) if total_clean > 0 else 0
        
        assert match_rate == 100.0, \
            f"Clean scenario match rate: {match_rate:.1f}% (expected 100%)"


def test_summary_table(reconciliation_results: List[ReconciliationResult], ground_truth: Dict):
    """Print a summary table of status counts."""
    print("\n" + "=" * 70)
    print("RECONCILIATION TEST SUMMARY")
    print("=" * 70)
    
    # Count statuses
    status_counts = defaultdict(int)
    for r in reconciliation_results:
        status_counts[r.status.value] += 1
    
    # Count ground truth scenarios
    scenario_counts = defaultdict(int)
    for data in ground_truth.values():
        scenario_counts[data["scenario"]] += 1
    
    print("\nStatus distribution:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status:20s}: {count:3d}")
    
    print("\nGround truth scenario distribution:")
    for scenario, count in sorted(scenario_counts.items()):
        print(f"  {scenario:20s}: {count:3d}")
    
    # Match rate
    order_results = [r for r in reconciliation_results if not r.order_id.startswith("ORPHAN-")]
    matched = sum(1 for r in order_results if r.status == MatchStatus.matched)
    total = len(order_results)
    match_rate = (matched / total * 100) if total > 0 else 0
    
    print(f"\nOverall match rate: {matched}/{total} ({match_rate:.1f}%)")
    
    # Clean scenario match rate
    clean_order_ids = [oid for oid, data in ground_truth.items() if data["scenario"] == "clean"]
    result_map = {r.order_id: r for r in reconciliation_results}
    clean_matched = sum(
        1 for oid in clean_order_ids
        if result_map.get(oid) and result_map[oid].status == MatchStatus.matched
    )
    clean_total = len(clean_order_ids)
    clean_rate = (clean_matched / clean_total * 100) if clean_total > 0 else 0
    
    print(f"Clean scenario match rate: {clean_matched}/{clean_total} ({clean_rate:.1f}%)")
    print("=" * 70)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
