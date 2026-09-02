"""
categorize.py — RAG-grounded categorization agent for SettleTrace.

Takes reconciliation results that need review and uses the LLM + knowledge base
to provide human-readable explanations with policy citations.
"""

from __future__ import annotations

import copy
import json
from typing import Dict, Any, Optional

from app.knowledge_base import retrieve, all_topics
from app.model import call_llm, parse_llm_response


def explain_exception(recon_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Explain a reconciliation exception using LLM + knowledge base.

    Takes a reconciliation result where status != 'matched', identifies the most
    relevant KB topic from the audit trail, retrieves the policy passage, and
    asks the LLM to provide a detailed explanation with citation.

    Parameters
    ----------
    recon_result : dict
        A reconciliation result dict (from reconcile.py) with status != 'matched'.
        Must have keys: order_id, status, audit_trail, etc.

    Returns
    -------
    dict
        A copy of recon_result with updated fields:
        - exception_reason: LLM-determined reason
        - confidence: LLM confidence score
        - llm_explanation: Human-readable explanation
        - cited_rule: KB passage ID that was referenced
        - audit_trail: Original trail + one line showing agent conclusion
    """
    # Defensive copy
    result = copy.deepcopy(recon_result)

    # Skip if already matched (shouldn't happen, but be safe)
    if result.get('status') == 'matched':
        return result

    # Extract audit trail text for analysis
    audit_trail = result.get('audit_trail', [])
    if not audit_trail:
        # No audit trail to analyze — return with minimal LLM explanation
        result.update({
            'exception_reason': 'unknown',
            'confidence': 0.1,
            'llm_explanation': 'No audit trail available for analysis',
            'cited_rule': '',
        })
        return result

    # Combine audit trail into searchable text
    audit_text = ' '.join(audit_trail)

    # Identify the most relevant KB topic by keyword matching
    kb_topic = _identify_kb_topic(audit_text, result.get('status', ''))

    # Retrieve the knowledge base passage
    if kb_topic:
        kb_passages = retrieve(kb_topic, top_k=1)
        kb_passage = kb_passages[0] if kb_passages else None
    else:
        kb_passage = None

    # Build prompt for the LLM
    prompt = _build_llm_prompt(result, audit_text, kb_passage)
    system_prompt = _build_system_prompt()

    # Call LLM
    llm_response = call_llm(prompt, system_prompt)
    parsed_response = parse_llm_response(llm_response)

    # Extract LLM outputs
    llm_reason = parsed_response.get('reason', 'unknown')
    llm_confidence = float(parsed_response.get('confidence', 0.5))
    llm_explanation = parsed_response.get('explanation', 'LLM analysis unavailable')

    # Cited rule = KB passage ID if one was used
    cited_rule = kb_passage['id'] if kb_passage else ''

    # Update result
    result.update({
        'exception_reason': llm_reason,
        'confidence': llm_confidence,
        'llm_explanation': llm_explanation,
        'cited_rule': cited_rule,
    })

    # Add agent conclusion to audit trail
    conclusion = (
        f"Agent conclusion: {llm_reason} (confidence: {llm_confidence:.2f}) "
        f"citing {cited_rule if cited_rule else 'no specific rule'}"
    )
    result['audit_trail'].append(conclusion)

    return result


def _identify_kb_topic(audit_text: str, status: str) -> Optional[str]:
    """
    Identify the most relevant KB topic by matching keywords in audit trail.

    This is a simple heuristic — could be replaced with embeddings later.
    Order matters: more specific/unambiguous patterns should be checked first.
    """
    audit_lower = audit_text.lower()

    # Topic keyword mappings, ordered by specificity:
    # 1. Most specific patterns (least likely to false-match)
    # 2. Refund-related before generic "fee" (avoid false matches on "fee" in "refund" contexts)
    # 3. Fallback patterns
    topic_keywords_ordered = [
        ('settlement_lag', ['days after settlement', 'delayed', 't+3', 't+4', 't+5', 't+6', 't+7']),
        ('duplicate_batch', ['duplicate', 'same utr', 'multiple credits', 'overlapping utrs']),
        ('orphan_bank_credit', ['orphan', 'no matching settlement', 'unmatched credit']),
        ('missing_bank_credit', ['no bank credit', 'no credit found', 'missing']),
        ('refund_not_netted', ['shortage', 'short by', 'unexplained', 'refund']),  # Before partial_hold to avoid false match on "reserve"
        ('partial_hold', ['partial_hold', 'withheld', 'reserve']),
        ('fee_mismatch', ['fee mismatch', 'fee variance', 'deviat', 'threshold']),
        ('currency_rounding', ['rounding', 'paise', 'floating point']),
        ('gl_account_mapping', ['account', 'gl']),
    ]

    # Status-based hints if audit trail is ambiguous
    status_hints = {
        'settlement_lag': 'settlement_lag',
        'partial_hold': 'partial_hold',
        'needs_review': None,  # Could be many things
        'unresolved': 'missing_bank_credit',  # Often missing credits
    }

    # Check keywords first (in priority order)
    for topic, keywords in topic_keywords_ordered:
        if any(kw in audit_lower for kw in keywords):
            return topic

    # Fall back to status hint
    return status_hints.get(status)


def _build_llm_prompt(result: Dict[str, Any], audit_text: str, kb_passage: Optional[Dict[str, str]]) -> str:
    """Build the prompt for the LLM with all relevant context."""
    
    # Extract key facts (exclude audit_trail to avoid duplication)
    facts = {k: v for k, v in result.items() if k != 'audit_trail'}
    facts_json = json.dumps(facts, indent=2, default=str)

    # Build prompt sections
    prompt_parts = [
        "You are a Razorpay settlement reconciliation expert. Analyze this exception:",
        "",
        "RECONCILIATION FACTS:",
        facts_json,
        "",
        "AUDIT TRAIL:",
        audit_text,
        "",
    ]

    # Add KB passage if available
    if kb_passage:
        prompt_parts.extend([
            "RELEVANT POLICY:",
            f"[{kb_passage['id']}] {kb_passage['text']}",
            "",
        ])

    prompt_parts.extend([
        "Based on the facts, audit trail, and policy (if provided), determine:",
        "1. The most accurate exception_reason from the standard list",
        "2. Your confidence level (0.0 = very uncertain, 1.0 = very certain)",
        "3. A clear explanation of what happened and why",
        "",
        "IMPORTANT RULES:",
        "- NEVER invent numbers not present in the input",
        "- If no policy clearly applies, return reason='unknown' with low confidence",
        "- Focus on the root cause, not symptoms",
        "- Be specific about which amounts/dates/UTRs support your conclusion",
    ])

    return "\n".join(prompt_parts)


def _build_system_prompt() -> str:
    """Build the system prompt for the LLM."""
    return (
        "You are a Razorpay settlement reconciliation expert with deep knowledge of "
        "payment processing, banking operations, and financial reconciliation policies. "
        
        "Your role is to analyze reconciliation exceptions and provide accurate, "
        "policy-grounded explanations for each discrepancy. "
        
        "Standard exception reasons: fee_mismatch, gst_mismatch, refund_not_netted, "
        "duplicate_batch, missing_bank_credit, orphan_bank_credit, currency_rounding, "
        "settlement_lag, partial_hold, unknown. "
        
        "You MUST respond with valid JSON in this exact format:\n"
        '{"reason": "<exception_reason>", "confidence": 0.0-1.0, "explanation": "..."}\n'
        
        "CRITICAL: Never invent amounts, dates, or UTRs not present in the input. "
        "If you cannot confidently determine the reason, use 'unknown' with low confidence."
    )


def categorize_batch(recon_results: list) -> list:
    """
    Categorize a batch of reconciliation results.

    Convenience function to process multiple results at once.

    Parameters
    ----------
    recon_results : list
        List of reconciliation result dicts.

    Returns
    -------
    list
        List of categorized results (only non-matched ones are processed).
    """
    categorized = []
    
    for result in recon_results:
        if result.get('status') == 'matched':
            # Already resolved, no need for LLM analysis
            categorized.append(result)
        else:
            # Needs explanation
            categorized.append(explain_exception(result))
    
    return categorized