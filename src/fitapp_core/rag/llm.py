# src/fitapp_core/rag/llm.py
from __future__ import annotations

import os
import re
import json
import time
import pathlib
import datetime
from typing import Any, Dict, Optional

from openai import OpenAI
from dotenv import load_dotenv

# -------------------------
# Env + client
# -------------------------
load_dotenv(dotenv_path=".env.local")

BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.perplexity.ai")
MODEL = os.getenv("PERPLEXITY_MODEL", "sonar-pro")
API_KEY = os.getenv("PERPLEXITY_API_KEY")

_client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# -------------------------
# Local JSONL logging
# -------------------------
LOG_DIR = pathlib.Path("./data/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

def _log_file_path() -> pathlib.Path:
    return LOG_DIR / f"llm_{datetime.date.today().isoformat()}.jsonl"

def _json_safe(v: Any) -> Any:
    if v is None or isinstance(v, (str, int, float, bool)):
        return v
    if isinstance(v, (list, tuple, set)):
        return [_json_safe(x) for x in v]
    if isinstance(v, dict):
        return {str(k): _json_safe(val) for k, val in v.items()}
    try:
        # numpy scalars/arrays and pandas NA
        import numpy as np  # type: ignore
        if isinstance(v, np.ndarray):
            return v.tolist()
        if isinstance(v, (np.integer, np.floating, np.bool_)):
            return v.item()
    except Exception:
        pass
    try:
        import pandas as pd  # type: ignore
        if isinstance(v, (pd._libs.missing.NAType,)):  # type: ignore[attr-defined]
            return None
        if isinstance(v, (float, str)) and pd.isna(v):
            return None
    except Exception:
        pass
    # Fallback
    return str(v)

def _log_event(event: Dict[str, Any]) -> None:
    try:
        safe = {str(k): _json_safe(v) for k, v in event.items()}
        with _log_file_path().open("a", encoding="utf-8") as f:
            f.write(json.dumps(safe, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[LLM-LOG] failed: {e}")

# -------------------------
# Parsing helpers
# -------------------------
def _strip_code_fences(text: str) -> str:
    t = (text or "").strip()
    # Remove an opening fence like ``````JSONC / ```
    t = re.sub(r"^\s*```[A-Za-z0-9_+\-]*\s*\n?", "", t)
    # Remove a trailing closing fence like ```
    t = re.sub(r"\n?\s*```\s*$", "", t)
    return t.strip()

def _balanced_json_slice(text: str) -> Optional[str]:
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None

def _repair_json(s: str) -> str:
    s = s.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    # Replace single quotes with double quotes when not escaped
    s = re.sub(r"(?<!\\)'", '"', s)
    # Remove trailing commas before } or ]
    s = re.sub(r",\s*([}\]])", r"\1", s)
    return s.strip()

def _parse_object_text(text: str) -> Dict[str, Any]:
    t = _strip_code_fences(text)
    cand = _balanced_json_slice(t) or t
    attempts = [
        cand,
        _repair_json(cand),
        _balanced_json_slice(_repair_json(cand)) or "",
    ]
    for payload in attempts:
        if not payload:
            continue
        try:
            obj = json.loads(payload)
            if isinstance(obj, dict):
                return obj
        except Exception:
            pass
    print("[LLM] Object parse failed after repair; returning empty fallback")
    return {}

def _extract_choice_text(resp: Any) -> str:
    # OpenAI SDK objects
    try:
        msg = resp.choices[0].message
        content = getattr(msg, "content", "")
        if isinstance(content, list):
            return "".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in content
            )
        return str(content or "")
    except Exception:
        pass
    # Dict-shaped response (provider variants)
    try:
        ch = resp["choices"][0] if isinstance(resp, dict) else resp.choices[0]
        msg = ch.get("message", {}) if isinstance(ch, dict) else {}
        content = msg.get("content", "") if isinstance(msg, dict) else ""
        if isinstance(content, list):
            return "".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in content
            )
        if content:
            return str(content)
        if isinstance(ch, dict) and "text" in ch:
            return str(ch["text"])
    except Exception:
        pass
    return ""

# -------------------------
# Public API (with logging)
# -------------------------
def call_llm_json_object_with_log(
    prompt: str,
    schema: Dict[str, Any],
    context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Ask the model for a single JSON object; tolerate stray prose and minor JSON defects.
    Also logs a structured JSONL line with metadata and the first ~2KB of the raw completion.
    """
    sys_msg = "Return ONLY a JSON object. No prose."
    t0 = time.time()
    usage: Dict[str, Any] = {}
    raw1 = ""
    raw2 = ""
    try:
        resp = _client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=1000,
        )
        raw1 = _extract_choice_text(resp)
        obj = _parse_object_text(raw1)
        # usage (best effort)
        try:
            u = getattr(resp, "usage", {}) or {}
            usage = dict(u) if isinstance(u, dict) else {}
        except Exception:
            usage = {}

        if obj:
            _log_event(
                {
                    "ts": datetime.datetime.utcnow().isoformat() + "Z",
                    "event": "llm_json_ok",
                    "model": MODEL,
                    "elapsed_ms": int((time.time() - t0) * 1000),
                    "usage": usage,
                    "context": context,
                    "raw_head": raw1[:2000],
                    "parse_ok": True,
                }
            )
            return obj

        # One gentle retry with stronger JSON instruction
        resp2 = _client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": sys_msg + " Respond with a single JSON object only.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=1000,
        )
        raw2 = _extract_choice_text(resp2)
        obj2 = _parse_object_text(raw2)
        try:
            u2 = getattr(resp2, "usage", {}) or {}
            if isinstance(u2, dict):
                usage.update({f"retry_{k}": v for k, v in u2.items()})
        except Exception:
            pass

        _log_event(
            {
                "ts": datetime.datetime.utcnow().isoformat() + "Z",
                "event": "llm_json_retry" if obj2 else "llm_json_fail",
                "model": MODEL,
                "elapsed_ms": int((time.time() - t0) * 1000),
                "usage": usage,
                "context": context,
                "raw_head": (raw2 or raw1)[:2000],
                "parse_ok": bool(obj2),
                "error": None if obj2 else "object-parse-failed",
            }
        )
        return obj2 if isinstance(obj2, dict) else {}
    except Exception as e:
        _log_event(
            {
                "ts": datetime.datetime.utcnow().isoformat() + "Z",
                "event": "llm_json_error",
                "model": MODEL,
                "elapsed_ms": int((time.time() - t0) * 1000),
                "usage": usage,
                "context": context,
                "raw_head": (raw2 or raw1)[:2000],
                "parse_ok": False,
                "error": str(e),
            }
        )
        print(f"[LLM] Request error: {e}; returning empty object")
        return {}

def call_llm_json_object(prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Backward-compatible wrapper that logs with an empty context.
    Prefer call_llm_json_object_with_log to pass goal/days/retrieval info.
    """
    return call_llm_json_object_with_log(prompt, schema, context={})

# Back-compat alias used by older code/tests
def call_llm_json(prompt: str) -> Dict[str, Any]:
    return call_llm_json_object(prompt, schema={})
