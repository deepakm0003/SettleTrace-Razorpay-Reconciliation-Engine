"""
main.py — FastAPI application for SettleTrace.

Exposes reconciliation + categorization pipeline as REST API endpoints.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.reconcile import load_orders, load_settlements, load_bank_credits, run_reconciliation
from app.categorize import explain_exception
from app.evaluate import (
    load_ground_truth,
    convert_results_to_dicts,
    calculate_reconciliation_match_rate,
    calculate_classification_accuracy,
    calculate_confidence_coverage,
    find_unresolved_cases,
    write_metrics_json,
)


# ---------------------------------------------------------------------------
# FastAPI app setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="SettleTrace API",
    description="Razorpay settlement reconciliation with RAG-grounded categorization",
    version="1.0.0",
)

# CORS middleware for frontend (Vite default port)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# In-memory cache
# ---------------------------------------------------------------------------

_CACHE: Dict[str, Any] = {
    "results": None,
    "timestamp": None,
}

DATA_DIR = Path(__file__).parent.parent / "data"


# ---------------------------------------------------------------------------
# Pydantic models for responses
# ---------------------------------------------------------------------------

class ReconciliationResult(BaseModel):
    order_id: str
    status: str
    matched_settlement_id: Optional[str]
    matched_bank_credit_id: Optional[str]
    expected_net: float
    actual_net: float
    delta: float
    exception_reason: Optional[str]
    llm_explanation: str
    cited_rule: str
    confidence: float
    audit_trail: List[str]


class MetricsResponse(BaseModel):
    timestamp: str
    reconciliation_metrics: Dict[str, Any]
    classification_metrics: Dict[str, Any]
    confidence_metrics: Dict[str, Any]
    unresolved_cases_count: int
    unresolved_cases: List[Dict[str, Any]]


class ExceptionItem(BaseModel):
    order_id: str
    status: str
    exception_reason: Optional[str]
    confidence: float
    expected_net: float
    actual_net: float
    delta: float
    llm_explanation: str
    cited_rule: str


class RefreshResponse(BaseModel):
    message: str
    results_count: int
    timestamp: str


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _load_and_categorize() -> List[Dict[str, Any]]:
    """Load data, run reconciliation, and categorize exceptions."""
    # Load data
    orders = load_orders(DATA_DIR / "orders_ledger.csv")
    settlements = load_settlements(DATA_DIR / "razorpay_settlements.csv")
    bank_credits = load_bank_credits(DATA_DIR / "bank_statement.csv")
    
    # Run reconciliation
    reconcile_results = run_reconciliation(orders, settlements, bank_credits)
    
    # Convert to dicts
    result_dicts = convert_results_to_dicts(reconcile_results)
    
    # Filter to order-level results (exclude orphan pseudo-results for main API)
    order_results = [r for r in result_dicts if not r["order_id"].startswith("ORPHAN-")]
    
    # Identify results needing agent review
    needs_agent = []
    deterministic = []
    
    for result in order_results:
        status = result["status"]
        if status in ["matched", "settlement_lag", "partial_hold"]:
            deterministic.append(result)
        else:
            needs_agent.append(result)
    
    # Run categorization agent on exceptions
    if needs_agent:
        categorized = []
        for result in needs_agent:
            explained = explain_exception(result)
            categorized.append(explained)
        
        final_results = deterministic + categorized
    else:
        final_results = deterministic
    
    return final_results


def _ensure_metrics_exist() -> Path:
    """Ensure metrics.json exists and is reasonably fresh. Run evaluate if needed."""
    metrics_path = DATA_DIR / "metrics.json"
    
    # Check if exists and is fresh (less than 1 hour old for this demo)
    if metrics_path.exists():
        mtime = datetime.fromtimestamp(metrics_path.stat().st_mtime)
        age_seconds = (datetime.now() - mtime).total_seconds()
        
        if age_seconds < 3600:  # 1 hour
            return metrics_path
    
    # Need to regenerate
    print("Regenerating metrics.json...")
    
    # Run evaluation (imports here to avoid circular dependency at module level)
    from app.evaluate import run_full_pipeline
    
    final_results, ground_truth = run_full_pipeline()
    
    # Calculate metrics
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
    
    write_metrics_json(metrics, metrics_path)
    
    return metrics_path


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "app": "SettleTrace API",
        "version": "1.0.0",
        "endpoints": {
            "GET /reconcile": "Run full reconciliation pipeline",
            "POST /reconcile/refresh": "Clear cache and re-run pipeline",
            "GET /metrics": "Get evaluation metrics",
            "GET /exceptions": "Get non-matched results (lowest confidence first)",
            "GET /audit-trail/{order_id}": "Get full audit trail for one order",
        },
        "cache_status": "loaded" if _CACHE["results"] is not None else "empty",
    }


@app.get("/reconcile", response_model=List[ReconciliationResult], tags=["Reconciliation"])
async def get_reconciliation_results():
    """
    Run the full reconciliation + categorization pipeline.
    
    Returns all order results with LLM explanations for exceptions.
    Uses in-memory cache — results are only recomputed on cache refresh.
    """
    # Check cache
    if _CACHE["results"] is not None:
        return _CACHE["results"]
    
    # Run pipeline
    results = _load_and_categorize()
    
    # Cache results
    _CACHE["results"] = results
    _CACHE["timestamp"] = datetime.now().isoformat()
    
    return results


@app.post("/reconcile/refresh", response_model=RefreshResponse, tags=["Reconciliation"])
async def refresh_reconciliation():
    """
    Clear cache and re-run the reconciliation pipeline.
    
    Use this to force a fresh computation after data changes.
    """
    # Clear cache
    _CACHE["results"] = None
    _CACHE["timestamp"] = None
    
    # Re-run pipeline
    results = _load_and_categorize()
    
    # Update cache
    _CACHE["results"] = results
    _CACHE["timestamp"] = datetime.now().isoformat()
    
    return RefreshResponse(
        message="Cache refreshed and pipeline re-run",
        results_count=len(results),
        timestamp=_CACHE["timestamp"],
    )


@app.get("/metrics", response_model=MetricsResponse, tags=["Metrics"])
async def get_metrics():
    """
    Get evaluation metrics from metrics.json.
    
    Regenerates metrics if file is missing or stale (older than 1 hour).
    """
    metrics_path = _ensure_metrics_exist()
    
    # Load and return
    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics_data = json.load(f)
    
    return MetricsResponse(**metrics_data)


@app.get("/exceptions", response_model=List[ExceptionItem], tags=["Exceptions"])
async def get_exceptions(min_confidence: Optional[float] = None):
    """
    Get non-matched results, sorted by confidence ascending (most uncertain first).
    
    Query Parameters:
    - min_confidence: Filter to cases with confidence >= this value (optional)
    """
    # Ensure results are loaded
    if _CACHE["results"] is None:
        results = _load_and_categorize()
        _CACHE["results"] = results
        _CACHE["timestamp"] = datetime.now().isoformat()
    else:
        results = _CACHE["results"]
    
    # Filter to non-matched
    exceptions = [
        r for r in results
        if r["status"] != "matched"
    ]
    
    # Filter by confidence if requested
    if min_confidence is not None:
        exceptions = [e for e in exceptions if e.get("confidence", 0.0) >= min_confidence]
    
    # Sort by confidence ascending (lowest first = most uncertain)
    exceptions.sort(key=lambda x: x.get("confidence", 0.0))
    
    # Convert to ExceptionItem format
    exception_items = []
    for exc in exceptions:
        exception_items.append(ExceptionItem(
            order_id=exc["order_id"],
            status=exc["status"],
            exception_reason=exc.get("exception_reason"),
            confidence=exc.get("confidence", 0.0),
            expected_net=exc.get("expected_net", 0.0),
            actual_net=exc.get("actual_net", 0.0),
            delta=exc.get("delta", 0.0),
            llm_explanation=exc.get("llm_explanation", ""),
            cited_rule=exc.get("cited_rule", ""),
        ))
    
    return exception_items


@app.get("/audit-trail/{order_id}", response_model=ReconciliationResult, tags=["Audit"])
async def get_audit_trail(order_id: str):
    """
    Get the full reconciliation result including audit trail for a specific order.
    
    Path Parameters:
    - order_id: The order ID to retrieve (e.g., ORD00001)
    """
    # Ensure results are loaded
    if _CACHE["results"] is None:
        results = _load_and_categorize()
        _CACHE["results"] = results
        _CACHE["timestamp"] = datetime.now().isoformat()
    else:
        results = _CACHE["results"]
    
    # Find the order
    for result in results:
        if result["order_id"] == order_id:
            return ReconciliationResult(**result)
    
    # Not found
    raise HTTPException(
        status_code=404,
        detail=f"Order {order_id} not found in reconciliation results"
    )


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache_loaded": _CACHE["results"] is not None,
        "data_dir": str(DATA_DIR),
    }


# ---------------------------------------------------------------------------
# Startup event
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    print("=" * 70)
    print("SettleTrace API starting...")
    print(f"Data directory: {DATA_DIR}")
    print(f"Cache status: {'empty (will load on first request)' if _CACHE['results'] is None else 'preloaded'}")
    print("API docs available at: http://localhost:8000/docs")
    print("=" * 70)
