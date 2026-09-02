"""
model.py — LLM interface for SettleTrace.

This is the ONLY file in the project allowed to make LLM API calls.
All agent logic routes through call_llm(), which provides two code paths:

1. OFFLINE MOCK (no API key) — deterministic keyword-based classification
2. REAL ANTHROPIC API (ANTHROPIC_API_KEY set) — Claude Sonnet 4 API

Both return the same JSON schema:
  {"reason": "...", "confidence": 0.0-1.0, "explanation": "..."}
"""

from __future__ import annotations

import json
import os
import re
from typing import Dict, Any


def call_llm(prompt: str, system: str = "") -> str:
    """
    Call the LLM with a prompt and optional system message.

    Returns a JSON string:
      {"reason": "<exception_reason>", "confidence": 0.0-1.0, "explanation": "..."}

    If ANTHROPIC_API_KEY is not set, falls back to a deterministic mock
    that keyword-matches the prompt to assign a reason and confidence.
    This allows the entire project to run with zero API keys and zero cost.

    Parameters
    ----------
    prompt : str
        The user prompt describing the reconciliation discrepancy.
    system : str
        Optional system message (used only in real API calls).

    Returns
    -------
    str
        JSON string with reason, confidence, explanation.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()

    if api_key:
        return _call_anthropic(prompt, system, api_key)
    else:
        return _mock_llm(prompt)


# ---------------------------------------------------------------------------
# OFFLINE MOCK — deterministic keyword-based classification
# ---------------------------------------------------------------------------

def _mock_llm(prompt: str) -> str:
    """
    Deterministic mock LLM that pattern-matches keywords in the prompt.

    This ensures the project is fully runnable offline with zero API cost.
    
    Note: Confidence values are calibrated based on the mock's known accuracy:
    - High confidence (0.90+): patterns the mock recognizes well (duplicate_batch, settlement_lag)
    - Medium confidence (0.75-0.85): patterns with moderate accuracy
    - Low confidence (0.45-0.50): patterns known to be problematic (refund_not_netted, which
      the mock often confuses with partial_hold due to "reserve" keyword matching)
    """
    prompt_lower = prompt.lower()

    # Keyword patterns for each exception reason (order matters — most specific first)
    patterns = [
        # (reason, keywords, confidence)
        ("settlement_lag", ["settlement_lag", "t+3", "t+4", "t+5", "t+6", "t+7", "days after settlement", "late credit", "delayed"], 0.95),
        ("duplicate_batch", ["duplicate", "same utr", "multiple credits", "two credits"], 0.93),
        ("orphan_bank_credit", ["orphan", "no settlement", "unmatched credit", "no batch", "no matching settlement"], 0.88),
        ("missing_bank_credit", ["missing", "no bank credit", "no credit found"], 0.87),
        ("partial_hold", ["partial_hold", "reserve", "withheld", "hold"], 0.92),
        ("fee_mismatch", ["fee_mismatch", "fee variance", "deviat", "threshold"], 0.90),
        # Refund patterns: LOW confidence (0.45) because the mock is known to misclassify
        # refund_not_netted as fee_mismatch or partial_hold due to keyword overlap
        ("refund_not_netted", ["refund", "netted", "possible refund", "outside reserve", "shortage", "short by"], 0.45),
        ("currency_rounding", ["rounding", "paise", "floating point", "residual"], 0.80),
        ("gst_mismatch", ["gst", "18%", "tax"], 0.89),
    ]

    # Match keywords in order of specificity
    for reason, keywords, confidence in patterns:
        if any(kw in prompt_lower for kw in keywords):
            explanation = (
                f"Mock classification based on keyword presence. "
                f"Detected pattern: {reason}. "
                f"(Real LLM would provide detailed reasoning here.)"
            )
            return json.dumps({
                "reason": reason,
                "confidence": confidence,
                "explanation": explanation,
            })

    # Default fallback
    return json.dumps({
        "reason": "unknown",
        "confidence": 0.5,
        "explanation": (
            "Mock could not match any known pattern. "
            "Real LLM would analyze the full context."
        ),
    })


# ---------------------------------------------------------------------------
# REAL ANTHROPIC API — Claude Sonnet 4
# ---------------------------------------------------------------------------

def _call_anthropic(prompt: str, system: str, api_key: str) -> str:
    """
    Call the Anthropic API with Claude Sonnet 4 (claude-sonnet-4-20250514).

    Parameters
    ----------
    prompt : str
        User prompt.
    system : str
        System message.
    api_key : str
        Anthropic API key.

    Returns
    -------
    str
        JSON string from the model.
    """
    try:
        from anthropic import Anthropic
    except ImportError:
        raise RuntimeError(
            "anthropic package not installed. "
            "Run: pip install anthropic"
        )

    client = Anthropic(api_key=api_key)

    # Enforce JSON output format in system message
    if system:
        system += (
            "\n\nYou MUST respond with valid JSON in this exact format:\n"
            '{"reason": "<exception_reason>", "confidence": 0.0-1.0, "explanation": "..."}\n'
            "Do not include any text outside the JSON object."
        )
    else:
        system = (
            "You MUST respond with valid JSON in this exact format:\n"
            '{"reason": "<exception_reason>", "confidence": 0.0-1.0, "explanation": "..."}\n'
            "Do not include any text outside the JSON object."
        )

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        temperature=0.0,  # deterministic for reconciliation
        system=system,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    # Extract text from response
    content = response.content[0].text

    # Try to parse as JSON to validate format
    try:
        parsed = json.loads(content)
        # Ensure required keys exist
        if "reason" not in parsed or "confidence" not in parsed or "explanation" not in parsed:
            raise ValueError("Missing required JSON keys")
        return content
    except (json.JSONDecodeError, ValueError) as e:
        # Model didn't return valid JSON — wrap in error response
        return json.dumps({
            "reason": "unknown",
            "confidence": 0.0,
            "explanation": f"Model returned invalid JSON: {str(e)[:100]}. Raw: {content[:200]}",
        })


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def parse_llm_response(json_str: str) -> Dict[str, Any]:
    """
    Parse the JSON response from call_llm() into a dict.

    Parameters
    ----------
    json_str : str
        JSON string returned by call_llm().

    Returns
    -------
    dict
        Parsed dict with keys: reason, confidence, explanation.
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # Graceful fallback
        return {
            "reason": "unknown",
            "confidence": 0.0,
            "explanation": f"Failed to parse LLM response: {json_str[:100]}",
        }


def is_mock_mode() -> bool:
    """Return True if running in offline mock mode (no API key set)."""
    return not bool(os.environ.get("ANTHROPIC_API_KEY", "").strip())
