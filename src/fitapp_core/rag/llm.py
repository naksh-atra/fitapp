# import os
# import json
# from typing import Any, Dict, List

# from openai import OpenAI
# from dotenv import load_dotenv

# load_dotenv(dotenv_path=".env.local")

# BASE_URL = "https://api.perplexity.ai"
# MODEL = os.getenv("PERPLEXITY_MODEL", "sonar-pro")
# API_KEY = os.getenv("PERPLEXITY_API_KEY")

# _client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# SYSTEM_JSON_ONLY_V11 = (
#     "Return ONLY a JSON array of objects for a weekly workout plan; "
#     "no text outside the JSON."
# )

# PLAN_SCHEMA_V11 = {
#     "name": "plan_v11_schema",
#     "schema": {
#         "type": "array",
#         "items": {
#             "type": "object",
#             "properties": {
#                 "week_label": {"type": ["string", "null"]},
#                 "day": {"type": ["integer", "string"]},
#                 "day_name": {"type": ["string", "null"]},
#                 "block_type": {
#                     "type": ["string", "null"],
#                     "enum": ["main", "accessory", "prehab", "cardio_notes", None],
#                 },
#                 "movement": {"type": "string"},
#                 "main_focus": {"type": ["string", "null"]},
#                 "intensity_cue": {"type": ["string", "null"]},
#                 "sets": {"type": ["integer", "string", "null"]},
#                 "reps": {"type": ["integer", "string", "null"]},
#                 "duration": {"type": ["integer", "string", "null"]},
#                 "tempo_or_rest": {"type": ["string", "null"]},
#                 "notes": {"type": ["string", "null"]},
#             },
#             "required": ["day", "movement"],
#             "additionalProperties": False,
#         },
#     },
# }

# def _coerce_int_from_str(value: Any) -> Any:
#     if isinstance(value, int) or value is None:
#         return value
#     if isinstance(value, str):
#         digits = "".join(ch for ch in value if ch.isdigit())
#         if digits:
#             try:
#                 return int(digits)
#             except Exception:
#                 return value
#     return value

# def _extract_balanced_json_array(text: str) -> str:
#     """
#     Return the first complete top-level JSON array substring from text.
#     Tracks string/escape state to avoid cutting inside quoted strings.
#     """
#     in_string = False
#     escape = False
#     depth = 0
#     start = -1
#     for i, ch in enumerate(text):
#         if in_string:
#             if escape:
#                 escape = False
#             elif ch == "\\":
#                 escape = True
#             elif ch == '"':
#                 in_string = False
#             continue
#         else:
#             if ch == '"':
#                 in_string = True
#                 continue
#             if ch == '[':
#                 if depth == 0:
#                     start = i
#                 depth += 1
#             elif ch == ']':
#                 if depth > 0:
#                     depth -= 1
#                     if depth == 0 and start != -1:
#                         return text[start:i+1]
#     # No balanced array found; return original text (will likely fail parse -> fallback)
#     return text

# def call_llm_json(user_prompt: str) -> List[Dict[str, Any]]:
#     resp = _client.chat.completions.create(
#         model=MODEL,
#         temperature=0,
#         messages=[
#             {"role": "system", "content": SYSTEM_JSON_ONLY_V11},
#             {"role": "user", "content": user_prompt},
#         ],
#         response_format={"type": "json_schema", "json_schema": PLAN_SCHEMA_V11},
#         max_tokens=2000,
#     )
#     raw_content = resp.choices[0].message.content or ""
#     print("RAW RESPONSE >>>")
#     print(raw_content)

#     data: List[Dict[str, Any]] | None = None

#     # Attempt 1: strict JSON
#     try:
#         data = json.loads(raw_content)
#     except json.JSONDecodeError:
#         data = None

#     # Attempt 2: extract a balanced top-level array
#     if data is None:
#         try:
#             balanced = _extract_balanced_json_array(raw_content)
#             data = json.loads(balanced)
#         except Exception:
#             data = None

#     # Attempt 3: optional tolerant parser (json5) on balanced slice
#     if data is None:
#         try:
#             import json5  # optional dependency
#             balanced = _extract_balanced_json_array(raw_content)
#             data = json5.loads(balanced)
#         except Exception:
#             data = None

#     # Final fail-soft: avoid crashing UI; return empty list
#     if data is None:
#         print("[LLM] JSON parse failed; returning empty plan rows")
#         data = []

#     # Minimal coercions to help downstream sanitize/validation
#     for row in data:
#         if "day" in row:
#             row["day"] = _coerce_int_from_str(row.get("day"))
#         if "sets" in row:
#             row["sets"] = _coerce_int_from_str(row.get("sets"))
#         if "reps" in row:
#             row["reps"] = _coerce_int_from_str(row.get("reps"))
#     return data

# def call_llm_json_object(user_prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
#     resp = _client.chat.completions.create(
#         model=MODEL,
#         temperature=0,
#         messages=[
#             {"role": "system", "content": "Return ONLY a JSON object matching the provided schema."},
#             {"role": "user", "content": user_prompt},
#         ],
#         response_format={"type": "json_schema", "json_schema": {"name": "assessor", "schema": schema}},
#         max_tokens=500,
#     )
#     content = resp.choices[0].message.content or "{}"
#     return json.loads(content)










# src/fitapp_core/rag/llm.py
from __future__ import annotations
import os, re, json
from typing import Any, Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.local")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.perplexity.ai")
MODEL = os.getenv("PERPLEXITY_MODEL", "sonar-pro")
API_KEY = os.getenv("PERPLEXITY_API_KEY")
_client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


def _strip_code_fences(text: str) -> str:
    t = (text or "").strip()
    # Remove an opening fence like ```json or ```
    t = re.sub(r"^\s*```(?:json)?", "", t, flags=re.IGNORECASE)
    # Remove a trailing closing fence ```
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
    s = re.sub(r"(?<!\\)'", '"', s)
    s = re.sub(r",\s*([}\]])", r"\1", s)
    return s.strip()

def _parse_object_text(text: str) -> Dict[str, Any]:
    t = _strip_code_fences(text)
    cand = _balanced_json_slice(t) or t
    for payload in (cand, _repair_json(cand), _balanced_json_slice(_repair_json(cand)) or ""):
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
    try:
        # OpenAI SDK objects
        msg = resp.choices[0].message
        content = getattr(msg, "content", "")
        if isinstance(content, list):
            return "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in content)
        return str(content or "")
    except Exception:
        pass
    try:
        # Dict-shaped response
        ch = resp["choices"][0] if isinstance(resp, dict) else resp.choices[0]
        # Perplexity sometimes returns message.content as list
        msg = ch.get("message", {}) if isinstance(ch, dict) else {}
        content = msg.get("content", "") if isinstance(msg, dict) else ""
        if isinstance(content, list):
            return "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in content)
        if content:
            return str(content)
        if "text" in ch:
            return str(ch["text"])
    except Exception:
        pass
    return ""

def call_llm_json_object(prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    sys_msg = "Return ONLY a JSON object. No prose."
    try:
        resp = _client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1000,
        )
        content = _extract_choice_text(resp)
        obj = _parse_object_text(content)
        if obj:
            return obj
        # One gentle retry
        resp2 = _client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": sys_msg + " Respond with a single JSON object only."}, {"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1000,
        )
        content2 = _extract_choice_text(resp2)
        return _parse_object_text(content2)
    except Exception as e:
        print(f"[LLM] Request error: {e}; returning empty object")
        return {}

# Back-compat alias
def call_llm_json(prompt: str) -> Dict[str, Any]:
    return call_llm_json_object(prompt, schema={})
