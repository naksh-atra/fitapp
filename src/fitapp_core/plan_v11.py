# src/fitapp_core/plan_v11.py
from __future__ import annotations

from typing import Optional, List, Dict, Any
import re

from pydantic import ValidationError

from .models_v11 import InputsV11, PlanV11, PlanRowV11
from .models import PAL_MAP  # reuse existing PAL map from v1
from .energy import bmr_mifflin_st_jeor, tdee_from_bmr
from .rag.retriever import retrieve_snippets
from .rag.prompts import SYSTEM_PROMPT_V11, USER_TEMPLATE_V11
from .rag.llm import call_llm_json  # OpenAI-compatible client configured for the provider


# --- Helpers: robust parsing & normalization ---

DAY_NAMES = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"}

def _parse_int_lower_bound(val: Any) -> Optional[int]:
    """
    Coerce integers and simple ranges to an int (lower bound).
    Accepts: 8, "8", "3-6", "6–10" (en dash). Returns None if no integer found.
    """
    if isinstance(val, int):
        return val
    if isinstance(val, str):
        m = re.match(r"\s*(\d+)\s*(?:[-–]\s*\d+)?\s*$", val)
        if m:
            return int(m.group(1))
    return None


def _infer_block_type(day_counter: Dict[int, int]) -> str:
    """
    For rows missing block_type: first row per day -> 'main', others -> 'accessory'.
    """
    # caller increments before calling this; 1 means it's the first row for that day
    return "main" if list(day_counter.values())[-1] == 1 else "accessory"


def sanitize_rows(rows_json: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Make LLM-emitted rows conform to v1.1 requirements by:
      - Supplying missing required keys (week_label, day_name, block_type)
      - Coercing sets/reps to integers (lower bound of ranges)
      - Preserving optional fields when present
    """
    cleaned: List[Dict[str, Any]] = []
    per_day_seen: Dict[int, int] = {}

    for r in rows_json:
        # Day normalization
        day_raw = r.get("day", 1)
        try:
            day = int(day_raw)
        except Exception:
            day = 1
        per_day_seen[day] = per_day_seen.get(day, 0) + 1

        # Required v1.1 fields
        week_label = r.get("week_label") or "Week 1"
        day_name = r.get("day_name") or DAY_NAMES.get(day, f"Day {day}")
        block_type = r.get("block_type")
        if not block_type:
            block_type = "main" if per_day_seen[day] == 1 else "accessory"

        # Core fields
        movement = r.get("movement") or "Unknown"
        main_focus = r.get("main_focus")
        intensity_cue = r.get("intensity_cue")
        sets = _parse_int_lower_bound(r.get("sets"))
        reps = _parse_int_lower_bound(r.get("reps"))
        duration = r.get("duration")
        tempo_or_rest = r.get("tempo_or_rest")
        notes = r.get("notes")

        cleaned.append(
            {
                "week_label": week_label,
                "day": day,
                "day_name": day_name,
                "block_type": block_type,
                "movement": movement,
                "main_focus": main_focus,
                "intensity_cue": intensity_cue,
                "sets": sets,
                "reps": reps,
                "duration": duration,
                "tempo_or_rest": tempo_or_rest,
                "notes": notes,
            }
        )
    return cleaned


def _second_pass_repair(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Stricter repair:
      - Drop rows missing movement or day after sanitize
      - Force missing sets/reps to None (allowed) rather than invalid strings
    """
    repaired: List[Dict[str, Any]] = []
    for r in rows:
        if not isinstance(r.get("day"), int) or r.get("movement") in (None, "", "Unknown"):
            # keep Unknown but ensure it's a string
            r["movement"] = r.get("movement") or "Unknown"
        # Ensure optional numeric fields are None if not valid
        r["sets"] = r["sets"] if isinstance(r.get("sets"), int) else None
        r["reps"] = r["reps"] if isinstance(r.get("reps"), int) else None
        repaired.append(r)
    return repaired


# --- Entrypoint ---

def generate_plan_v11(inputs: InputsV11, tweak_note: Optional[str] = None) -> PlanV11:
    """
    Orchestrate a v1.1 plan:
      - Compute energy context
      - Retrieve optional snippets
      - Construct strict JSON-only prompt
      - Call LLM
      - Sanitize rows and validate into PlanRowV11
    Raises ValueError with a concise message if parsing irrecoverably fails.
    """
    pal_value = PAL_MAP[inputs.pal_code]
    bmr = bmr_mifflin_st_jeor(inputs.sex, inputs.weight_kg, inputs.height_cm, inputs.age)
    tdee = tdee_from_bmr(bmr, pal_value)

    # Optional grounding
    snippets = retrieve_snippets(inputs.model_dump())
    snippets_text = "\n".join(f"- [{s.get('id','doc')}]: {s['text']}" for s in snippets) or "- none"

    # Prompt assembly (system + user)
    user_prompt = USER_TEMPLATE_V11.format(
        sex=inputs.sex,
        age=inputs.age,
        height_cm=inputs.height_cm,
        weight_kg=inputs.weight_kg,
        pal_value=pal_value,
        goal=inputs.goal,
        equipment=inputs.equipment or [],
        bmr=bmr,
        tdee=tdee,
        snippets=snippets_text,
        tweak=tweak_note or "",
    )
    prompt = SYSTEM_PROMPT_V11 + "\n" + user_prompt

    # Call LLM (temperature 0 configured in the client; JSON-only instruction in system)
    raw_rows = call_llm_json(prompt)

    # First pass sanitize then validate
    rows_json = sanitize_rows(raw_rows)
    try:
        rows: List[PlanRowV11] = [PlanRowV11(**r) for r in rows_json]
    except ValidationError:
        # Second pass: stricter repair, then one more validation attempt
        repaired = _second_pass_repair(rows_json)
        try:
            rows = [PlanRowV11(**r) for r in repaired]
        except ValidationError as e:
            # Surface a concise error; UI should catch and show a friendly message
            raise ValueError(
                "Plan generation produced non-conforming rows after repair; please try again or adjust the tweak."
            ) from e

    # Ordering: week -> day -> section priority
    priority = {"main": 0, "accessory": 1, "prehab": 2, "cardio_notes": 3}
    rows.sort(key=lambda r: (r.week_label, r.day, priority.get(r.block_type, 9)))

    return PlanV11(goal=inputs.goal, rows=rows)
