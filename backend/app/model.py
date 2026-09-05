from __future__ import annotations

import json, os, re, time, threading
from itertools import cycle
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

NVIDIA_NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"

# Load API keys from environment variables
def _load_api_keys():
    """Load NVIDIA API keys from environment variables."""
    keys = []
    
    # Try to load from NVIDIA_API_KEY_1, NVIDIA_API_KEY_2, etc.
    i = 1
    while True:
        key = os.getenv(f"NVIDIA_API_KEY_{i}")
        model = os.getenv(f"NVIDIA_MODEL_{i}", "nvidia/nemotron-3-ultra-550b-a55b")
        if not key:
            break
        keys.append((key, model))
        i += 1
    
    # Fallback: single key from NVIDIA_API_KEY
    if not keys:
        single_key = os.getenv("NVIDIA_API_KEY")
        if single_key:
            keys.append((single_key, "nvidia/nemotron-3-ultra-550b-a55b"))
    
    if not keys:
        print("⚠️  WARNING: No NVIDIA API keys found in environment variables.")
        print("   Set NVIDIA_API_KEY_1, NVIDIA_API_KEY_2, etc. in .env file")
        print("   Falling back to mock mode for all classifications.")
    
    return keys

_KEY_POOL = _load_api_keys()
_pool_cycle = cycle(_KEY_POOL) if _KEY_POOL else None
_pool_lock  = threading.Lock()

MAX_RETRIES = 3
BASE_DELAY  = 2.0
CALL_DELAY  = 0.1


def _next_pair():
    with _pool_lock:
        if not _pool_cycle:
            return None, None
        return next(_pool_cycle)


def call_llm(prompt: str, system: str = "") -> str:
    return _call_with_retry(prompt, system)


# ── Retry wrapper ──────────────────────────────────────────────────────────

def _call_with_retry(prompt: str, system: str) -> str:
    # If no API keys available, use mock immediately
    if not _KEY_POOL:
        r = json.loads(_mock_llm(prompt))
        r["confidence"]  = min(r["confidence"], 0.3)
        r["explanation"] = "[No API keys] " + r["explanation"]
        return json.dumps(r)
    
    delay = BASE_DELAY
    last_err = None

    for attempt in range(1, MAX_RETRIES + 1):
        api_key, model = _next_pair()
        if not api_key:
            break
        try:
            time.sleep(CALL_DELAY)
            return _call_nvidia(prompt, system, api_key, model)
        except Exception as exc:
            last_err = exc
            err = str(exc).lower()
            retryable = any(k in err for k in [
                "overload", "503", "502", "500", "rate limit",
                "timeout", "connection", "temporarily", "try again", "429",
            ])
            if retryable and attempt < MAX_RETRIES:
                print(f"  [LLM] retry {attempt}/{MAX_RETRIES} "
                      f"({model.split('/')[-1][:20]}…) in {delay:.0f}s")
                time.sleep(delay)
                delay *= 2
            else:
                break

    print(f"  [LLM] exhausted — mock fallback")
    r = json.loads(_mock_llm(prompt))
    r["confidence"]  = min(r["confidence"], 0.3)
    r["explanation"] = "[API fail] " + r["explanation"]
    return json.dumps(r)


# ── NVIDIA NIM call — streaming, works for both models ────────────────────

def _call_nvidia(prompt: str, system: str, api_key: str, model: str) -> str:
    from openai import OpenAI

    client = OpenAI(base_url=NVIDIA_NIM_BASE_URL, api_key=api_key)

    valid_reasons = (
        "settlement_lag | duplicate_batch | orphan_bank_credit | missing_bank_credit | "
        "fee_mismatch | gst_mismatch | partial_hold | refund_not_netted | "
        "currency_rounding | unknown"
    )
    json_schema = '{"reason":"<valid reason>","confidence":<0.0-1.0>,"explanation":"<text>"}'
    system_msg = (
        (system + "\n\n" if system else "")
        + "You are a Razorpay settlement reconciliation expert. "
          "Classify the exception.\n\n"
        + f"Valid reasons: {valid_reasons}\n\n"
          "Output ONLY a single JSON object — no fences, no extra text:\n"
        + json_schema
    )

    # Model-specific params
    is_nemotron = "nemotron" in model
    extra = {"chat_template_kwargs": {"enable_thinking": True}} if is_nemotron else \
            {"chat_template_kwargs": {"thinking": True, "reasoning_effort": "high"}}

    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user",   "content": prompt},
        ],
        temperature=1,
        top_p=0.95,
        max_tokens=2048,
        extra_body=extra,
        stream=True,
    )

    thinking_parts, answer_parts = [], []
    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        r = getattr(delta, "reasoning_content", None) or getattr(delta, "reasoning", None)
        if r:
            thinking_parts.append(r)
        if delta.content:
            answer_parts.append(delta.content)

    thinking = "".join(thinking_parts).strip()
    answer   = "".join(answer_parts).strip()
    clean    = _strip_fences(answer)

    try:
        parsed = json.loads(clean)
        for k in ("reason", "confidence", "explanation"):
            if k not in parsed:
                raise ValueError(f"Missing key: {k}")
        if thinking:
            short = thinking[:150] + ("…" if len(thinking) > 150 else "")
            parsed["explanation"] += f"\n\n[AI thinking]: {short}"
        return json.dumps(parsed)
    except (json.JSONDecodeError, ValueError) as e:
        ex = _extract_json(answer)
        if ex:
            return json.dumps(ex)
        return json.dumps({
            "reason": "unknown", "confidence": 0.0,
            "explanation": f"Parse error: {str(e)[:60]} | raw: {answer[:150]}",
        })


# ── Offline mock ───────────────────────────────────────────────────────────

def _mock_llm(prompt: str) -> str:
    p = prompt.lower()
    patterns = [
        ("settlement_lag",      ["settlement_lag","t+3","t+4","t+5","t+6","t+7","delayed"],           0.95),
        ("duplicate_batch",     ["duplicate","same utr","multiple credits","two credits"],             0.93),
        ("orphan_bank_credit",  ["orphan","no settlement","unmatched credit","no matching settlement"],0.88),
        ("missing_bank_credit", ["missing","no bank credit","no credit found"],                        0.87),
        ("fee_mismatch",        ["fee mismatch","fee variance","deviat","threshold"],                   0.90),
        ("gst_mismatch",        ["gst","18%","tax"],                                                   0.89),
        ("partial_hold",        ["partial_hold","reserve","withheld"],                                 0.92),
        ("refund_not_netted",   ["refund","netted","possible refund","shortage","short by"],            0.45),
        ("currency_rounding",   ["rounding","paise","floating point","residual"],                      0.80),
    ]
    for reason, keywords, confidence in patterns:
        if any(kw in p for kw in keywords):
            return json.dumps({"reason": reason, "confidence": confidence,
                               "explanation": f"Mock → {reason}."})
    return json.dumps({"reason": "unknown", "confidence": 0.5,
                       "explanation": "Mock: no pattern."})


# ── Helpers ────────────────────────────────────────────────────────────────

def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        inner = parts[1] if len(parts) > 1 else text
        return inner[4:].strip() if inner.startswith("json") else inner.strip()
    return text


def _extract_json(text: str) -> Dict[str, Any] | None:
    m = re.search(r'\{[^{}]*"reason"[^{}]*\}', text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            pass
    return None


def parse_llm_response(json_str: str) -> Dict[str, Any]:
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return {"reason": "unknown", "confidence": 0.0,
                "explanation": f"Parse error: {json_str[:100]}"}


def is_mock_mode() -> bool:
    return False
