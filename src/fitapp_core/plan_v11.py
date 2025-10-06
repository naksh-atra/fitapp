# # src/fitapp_core/plan_v11.py
# from __future__ import annotations

# from typing import Optional, List, Dict, Any
# import re

# from pydantic import ValidationError

# from .models_v11 import InputsV11, PlanV11, PlanRowV11
# from .models import PAL_MAP as PALMAP  # alias to match internal usage
# from .energy import bmr_mifflin_st_jeor, tdee_from_bmr
# from .rag.retriever import retrieve_snippets
# from .rag.prompts import (
#     SYSTEM_PROMPT_V11,
#     USER_TEMPLATE_V11,
#     render_snippets_for_v11,
#     TWEAK_ASSESSOR_SYSTEM,
#     TWEAK_ASSESSOR_USER,
#     render_numbered_snippets,
# )
# from .rag.llm import call_llm_json_object

# DAY_NAMES = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"}
# DAY_NAME_MAP = {
#     "mon": 1, "monday": 1, "tue": 2, "tuesday": 2, "wed": 3, "wednesday": 3,
#     "thu": 4, "thursday": 4, "fri": 5, "friday": 5, "sat": 6, "saturday": 6, "sun": 7, "sunday": 7,
# }

# def _parse_int_lower_bound(val: Any) -> Optional[int]:
#     if isinstance(val, int):
#         return val
#     if isinstance(val, str):
#         m = re.match(r"\s*(\d+)\s*(?:[-–]\s*\d+)?\s*$", val)
#         if m:
#             return int(m.group(1))
#     return None

# def _coerce_day(val: Any) -> int:
#     try:
#         return int(val)
#     except Exception:
#         if isinstance(val, str):
#             return DAY_NAME_MAP.get(val.strip().lower(), 1)
#         return 1

# def _make_retrieval_query(inputs: InputsV11) -> str:
#     goal = inputs.goal or ""
#     exp = getattr(inputs, "experience", "") or ""
#     days = getattr(inputs, "days_per_week", None)
#     equip_list = getattr(inputs, "equipment", None) or []
#     equip = ", ".join(equip_list) if isinstance(equip_list, list) else str(equip_list or "")
#     parts = [goal, exp]
#     if days:
#         parts.append(f"{days} days/week")
#     if equip:
#         parts.append(f"equipment: {equip}")
#     return ", ".join([p for p in parts if p]).strip(", ")

# # def _default_canonical_week(inputs: InputsV11) -> List[Dict[str, Any]]:
# #     # Minimal, safe templates by goal — ensures non-empty Week 1 if LLM fails
# #     dpw = getattr(inputs, "days_per_week", None) or 3
# #     dpw = max(2, min(6, int(dpw)))
# #     goal = (inputs.goal or "hypertrophy").lower()
# #     days = []
# #     def main_item(mv, s, r, notes=""):
# #         return {"movement": mv, "main_focus": None, "intensity_cue": "RPE 6–8", "sets": s, "reps": r, "tempo_or_rest": "60–90s", "notes": notes}
# #     def acc_item(mv, s, r, notes=""):
# #         return {"movement": mv, "sets": s, "reps": r, "tempo_or_rest": "45–75s", "notes": notes}
# #     split = [
# #         ("Mon", ["Squat", "Leg Press", "Leg Curl", "Calf Raise"]),
# #         ("Wed", ["Bench Press", "DB Row", "Incline DB Press", "Lat Pulldown"]),
# #         ("Fri", ["Deadlift", "Hamstring Curl", "Back Extension", "Plank"]),
# #     ]
# #     if dpw >= 4:
# #         split.append(("Thu", ["Overhead Press", "Lateral Raise", "Face Pull", "Triceps Pushdown"]))
# #     if dpw >= 5:
# #         split.append(("Tue", ["Pull Ups", "Seated Row", "Biceps Curl", "Reverse Fly"]))
# #     if goal in ("strength",):
# #         # Lower volume, strength focus
# #         base = []
# #         for name, items in split[:dpw]:
# #             main = [main_item(items, 3, 5, "technique focus")]
# #             acc = [acc_item(x, 3, 8) for x in items[1:3]]
# #             base.append({"day": name, "day_name": name, "main": main, "accessory": acc, "prehab": [], "cardio_notes": []})
# #         return base
# #     if goal in ("endurance",):
# #         base = []
# #         for name, _ in split[:dpw]:
# #             main = [{"movement": "Zone 2 Cardio", "duration": "30–45 min", "tempo_or_rest": "Zone 2", "notes": ""}]
# #             base.append({"day": name, "day_name": name, "main": [], "accessory": [], "prehab": [], "cardio_notes": main})
# #         return base
# #     if goal in ("fat_loss", "fat_loss"):
# #         base = []
# #         for name, items in split[:dpw]:
# #             main = [main_item(items, 3, 8, "steady pace")]
# #             acc = [acc_item(x, 3, 12) for x in items[1:3]]
# #             cardio = [{"movement": "Zone 2 Cardio", "duration": "20–30 min", "tempo_or_rest": "Zone 2", "notes": ""}]
# #             base.append({"day": name, "day_name": name, "main": main, "accessory": acc, "prehab": [], "cardio_notes": cardio})
# #         return base
# #     # hypertrophy default
# #     base = []
# #     for name, items in split[:dpw]:
# #         main = [main_item(items, 3, 8)]
# #         acc = [acc_item(x, 3, 10) for x in items[1:4]]
# #         base.append({"day": name, "day_name": name, "main": main, "accessory": acc, "prehab": [], "cardio_notes": []})
# #     return base

# # def _flatten_week(week_label: str, days: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
# #     out: List[Dict[str, Any]] = []
# #     for d in days or []:
# #         day = _coerce_day(d.get("day", 1))
# #         day_name = d.get("day_name") or DAY_NAMES.get(day, f"Day {day}")
# #         for section in ("main", "accessory", "prehab", "cardio_notes"):
# #             for item in (d.get(section) or []):
# #                 out.append({
# #                     "week_label": week_label,
# #                     "day": day,
# #                     "day_name": day_name,
# #                     "block_type": section,
# #                     "movement": item.get("movement", "Unknown"),
# #                     "main_focus": item.get("main_focus"),
# #                     "intensity_cue": item.get("intensity_cue"),
# #                     "sets": _parse_int_lower_bound(item.get("sets")),
# #                     "reps": _parse_int_lower_bound(item.get("reps")),
# #                     "duration": item.get("duration"),
# #                     "tempo_or_rest": item.get("tempo_or_rest"),
# #                     "notes": item.get("notes"),
# #                 })
# #     return out



# # src/fitapp_core/plan_v11.py — patch these two helpers and ensure PAL_MAP alias is present
# # from .models import PAL_MAP as PALMAP  # ensure this alias exists near the top

# def _default_canonical_week(inputs: InputsV11) -> List[Dict[str, Any]]:
#     dpw = getattr(inputs, "days_per_week", None) or 3
#     dpw = max(2, min(6, int(dpw)))
#     goal = (inputs.goal or "hypertrophy").lower()
#     days = []
#     def main_item(mv, s, r, notes=""):
#         return {"movement": mv, "main_focus": None, "intensity_cue": "RPE 6–8", "sets": s, "reps": r, "tempo_or_rest": "60–90s", "notes": notes}
#     def acc_item(mv, s, r, notes=""):
#         return {"movement": mv, "sets": s, "reps": r, "tempo_or_rest": "45–75s", "notes": notes}
#     split = [
#         ("Mon", ["Squat", "Leg Press", "Leg Curl", "Calf Raise"]),
#         ("Wed", ["Bench Press", "DB Row", "Incline DB Press", "Lat Pulldown"]),
#         ("Fri", ["Deadlift", "Hamstring Curl", "Back Extension", "Plank"]),
#     ]
#     if dpw >= 4:
#         split.append(("Thu", ["Overhead Press", "Lateral Raise", "Face Pull", "Triceps Pushdown"]))
#     if dpw >= 5:
#         split.append(("Tue", ["Pull Ups", "Seated Row", "Biceps Curl", "Reverse Fly"]))
#     prog_days = []
#     if goal == "strength":
#         for name, items in split[:dpw]:
#             main = [main_item(items[0], 3, 5, "technique focus")]
#             acc = [acc_item(items[1], 3, 8), acc_item(items[2], 3, 8)]
#             prog_days.append({"day": name, "day_name": name, "main": main, "accessory": acc, "prehab": [], "cardio_notes": []})
#         return prog_days
#     if goal == "endurance":
#         for name, _ in split[:dpw]:
#             cardio = [{"movement": "Zone 2 Cardio", "duration": "30–45 min", "tempo_or_rest": "Zone 2", "notes": ""}]
#             prog_days.append({"day": name, "day_name": name, "main": [], "accessory": [], "prehab": [], "cardio_notes": cardio})
#         return prog_days
#     if goal == "fat_loss":
#         for name, items in split[:dpw]:
#             main = [main_item(items[0], 3, 8, "steady pace")]
#             acc = [acc_item(items[1], 3, 12), acc_item(items[2], 3, 12)]
#             cardio = [{"movement": "Zone 2 Cardio", "duration": "20–30 min", "tempo_or_rest": "Zone 2", "notes": ""}]
#             prog_days.append({"day": name, "day_name": name, "main": main, "accessory": acc, "prehab": [], "cardio_notes": cardio})
#         return prog_days
#     # hypertrophy default
#     for name, items in split[:dpw]:
#         main = [main_item(items[0], 3, 8)]
#         acc = [acc_item(items[1], 3, 10), acc_item(items[2], 3, 10), acc_item(items[3], 3, 12)]
#         days.append({"day": name, "day_name": name, "main": main, "accessory": acc, "prehab": [], "cardio_notes": []})
#     return days

# def _flatten_week(week_label: str, days: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     out: List[Dict[str, Any]] = []
#     for d in days or []:
#         day = _coerce_day(d.get("day", 1))
#         day_name = d.get("day_name") or DAY_NAMES.get(day, f"Day {day}")
#         for section in ("main", "accessory", "prehab", "cardio_notes"):
#             items = d.get(section) or []
#             # Coerce strings/lists to dict items
#             coerced: List[Dict[str, Any]] = []
#             for it in items if isinstance(items, list) else [items]:
#                 if isinstance(it, dict):
#                     coerced.append(it)
#                 elif isinstance(it, str):
#                     coerced.append({"movement": it})
#                 elif isinstance(it, list):
#                     for mv in it:
#                         coerced.append({"movement": str(mv)})
#             for item in coerced:
#                 out.append({
#                     "week_label": week_label,
#                     "day": day,
#                     "day_name": day_name,
#                     "block_type": section,
#                     "movement": item.get("movement", "Unknown"),
#                     "main_focus": item.get("main_focus"),
#                     "intensity_cue": item.get("intensity_cue"),
#                     "sets": _parse_int_lower_bound(item.get("sets")),
#                     "reps": _parse_int_lower_bound(item.get("reps")),
#                     "duration": item.get("duration"),
#                     "tempo_or_rest": item.get("tempo_or_rest"),
#                     "notes": item.get("notes"),
#                 })
#     return out




# def _apply_progression_notes(rows: List[Dict[str, Any]], note: str) -> List[Dict[str, Any]]:
#     if not note:
#         return rows
#     out = []
#     for r in rows:
#         new_r = dict(r)
#         existing = (new_r.get("notes") or "").strip()
#         new_r["notes"] = (f"{existing} | {note}".strip(" |")) if existing else note
#         out.append(new_r)
#     return out

# def _sanitize_rows(rows_json: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     cleaned: List[Dict[str, Any]] = []
#     per_day_seen: Dict[int, int] = {}
#     for r in rows_json:
#         day = _coerce_day(r.get("day", 1))
#         per_day_seen[day] = per_day_seen.get(day, 0) + 1
#         week_label = r.get("week_label") or "Week 1"
#         day_name = r.get("day_name") or DAY_NAMES.get(day, f"Day {day}")
#         block_type = r.get("block_type") or ("main" if per_day_seen[day] == 1 else "accessory")
#         movement = r.get("movement") or "Unknown"
#         cleaned.append({
#             "week_label": week_label,
#             "day": day,
#             "day_name": day_name,
#             "block_type": block_type,
#             "movement": movement,
#             "main_focus": r.get("main_focus"),
#             "intensity_cue": r.get("intensity_cue"),
#             "sets": _parse_int_lower_bound(r.get("sets")),
#             "reps": _parse_int_lower_bound(r.get("reps")),
#             "duration": r.get("duration"),
#             "tempo_or_rest": r.get("tempo_or_rest"),
#             "notes": r.get("notes"),
#         })
#     return cleaned

# def _repair_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     repaired: List[Dict[str, Any]] = []
#     for r in rows:
#         if not isinstance(r.get("day"), int) or r.get("movement") in (None, "", "Unknown"):
#             r["movement"] = r.get("movement") or "Unknown"
#         r["sets"] = r["sets"] if isinstance(r.get("sets"), int) else None
#         r["reps"] = r["reps"] if isinstance(r.get("reps"), int) else None
#         repaired.append(r)
#     return repaired

# def assess_tweak(goal: str, tweak_text: str) -> Dict[str, Any]:
#     if not tweak_text or not tweak_text.strip():
#         return {"verdict": "ok", "rationale": "No tweak provided.", "citations": [], "sources": []}
#     hits = retrieve_snippets({"query": f"{goal}. Consider tweak: {tweak_text}", "evidence": "evidence", "top_k": 6})
#     numbered = render_numbered_snippets([h.get("text", "") for h in hits])
#     user = TWEAK_ASSESSOR_USER.format(goal=goal, tweak=tweak_text, snippets=numbered)
#     schema = {
#         "type": "object",
#         "properties": {
#             "verdict": {"type": "string", "enum": ["ok", "warn", "block"]},
#             "rationale": {"type": "string"},
#             "citations": {"type": "array", "items": {"type": "integer"}},
#         },
#         "required": ["verdict", "rationale", "citations"],
#         "additionalProperties": False,
#     }
#     out = call_llm_json_object(f"{TWEAK_ASSESSOR_SYSTEM}\n\n{user}", schema)
#     out["sources"] = [{"n": i + 1, "chunk_id": h.get("id"), "doc_id": h.get("doc_id")} for i, h in enumerate(hits)]
#     return out

# def generate_plan_v11(inputs: InputsV11, tweak_note: Optional[str] = None) -> PlanV11:
#     pal_value = PALMAP[inputs.pal_code]
#     bmr = bmr_mifflin_st_jeor(inputs.sex, inputs.weight_kg, inputs.height_cm, inputs.age)
#     tdee = tdee_from_bmr(bmr, pal_value)

#     # Retrieval (fail-soft)
#     retrieval_query = _make_retrieval_query(inputs)
#     try:
#         snippet_hits = retrieve_snippets({
#             "query": retrieval_query,
#             "domains": getattr(inputs, "domain_filters", None),
#             "evidence": "evidence",
#             "top_k": 6,
#         })
#     except Exception as e:
#         print(f"[Plan] RAG disabled or failed: {e}")
#         snippet_hits = []
#     snippets_text = render_snippets_for_v11([s.get("text", "") for s in snippet_hits]) if snippet_hits else "- none"

#     # Prompt
#     user_prompt = USER_TEMPLATE_V11.format(
#         sex=inputs.sex,
#         age=inputs.age,
#         height_cm=inputs.height_cm,
#         weight_kg=inputs.weight_kg,
#         pal_value=pal_value,
#         goal=inputs.goal,
#         equipment=inputs.equipment or [],
#         bmr=bmr,
#         tdee=tdee,
#         days_per_week=getattr(inputs, "days_per_week", None) or "",
#         snippets=snippets_text,
#         tweak=tweak_note or "",
#     )
#     prompt = SYSTEM_PROMPT_V11 + "\n" + user_prompt

#     # Expected object mode
#     schema = {"type": "object"}  # advisory; parsing is tolerant
#     compact = call_llm_json_object(prompt, schema) or {}

#     # Use canonical week if present; otherwise synthesize a safe default
#     canon_days = ((compact.get("canonical_week") or {}).get("days")) or []
#     if not canon_days:
#         print("[Plan] Using default canonical week fallback")
#         canon_days = _default_canonical_week(inputs)
#     prog_notes = {p.get("week"): p.get("note", "") for p in (compact.get("progression") or [])}

#     # Flatten Week 1
#     week1_rows = _flatten_week("Week 1", canon_days)

#     # Expand to weeks 2–4 with progression notes applied as text hints
#     rows_all: List[Dict[str, Any]] = []
#     rows_all += week1_rows
#     for wk in (2, 3, 4):
#         wk_rows = []
#         for r in week1_rows:
#             nr = dict(r)
#             nr["week_label"] = f"Week {wk}"
#             wk_rows.append(nr)
#         note = prog_notes.get(wk, "")
#         wk_rows = _apply_progression_notes(wk_rows, note)
#         rows_all += wk_rows

#     # Sanitize and validate
#     rows_json = _sanitize_rows(rows_all)
#     try:
#         rows: List[PlanRowV11] = [PlanRowV11(**r) for r in rows_json]
#     except ValidationError:
#         repaired = _repair_rows(rows_json)
#         rows = [PlanRowV11(**r) for r in repaired]

#     # Order rows for display/export
#     priority = {"main": 0, "accessory": 1, "prehab": 2, "cardio_notes": 3}
#     rows.sort(key=lambda r: (r.week_label, r.day, priority.get(r.block_type, 9)))

#     plan = PlanV11(goal=inputs.goal, rows=rows, week_count=4)
#     plan.extra = {
#         "snippets_count": len(snippet_hits),
#         "retrieved_snippets": snippet_hits[:6],
#         "retrieval_query": retrieval_query,
#     }
#     return plan



from __future__ import annotations

from typing import Optional, List, Dict, Any
import re

from pydantic import ValidationError

from .models_v11 import InputsV11, PlanV11, PlanRowV11
from .models import PAL_MAP as PALMAP
from .energy import bmr_mifflin_st_jeor, tdee_from_bmr
from .rag.retriever import retrieve_snippets
from .rag.prompts import (
    SYSTEM_PROMPT_V11,
    USER_TEMPLATE_V11,
    render_snippets_for_v11,
    TWEAK_ASSESSOR_SYSTEM,
    TWEAK_ASSESSOR_USER,
    render_numbered_snippets,
)
from .rag.llm import call_llm_json_object

DAY_NAMES = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"}
DAY_NAME_MAP = {
    "mon": 1, "monday": 1, "tue": 2, "tuesday": 2, "wed": 3, "wednesday": 3,
    "thu": 4, "thursday": 4, "fri": 5, "friday": 5, "sat": 6, "saturday": 6, "sun": 7, "sunday": 7,
}

def _parse_int_lower_bound(val: Any) -> Optional[int]:
    if isinstance(val, int):
        return val
    if isinstance(val, str):
        m = re.match(r"\s*(\d+)\s*(?:[-–]\s*\d+)?\s*$", val)
        if m:
            return int(m.group(1))
    return None

def _coerce_day(val: Any) -> int:
    try:
        return int(val)
    except Exception:
        if isinstance(val, str):
            return DAY_NAME_MAP.get(val.strip().lower(), 1)
        return 1

def _make_retrieval_query(inputs: InputsV11) -> str:
    goal = inputs.goal or ""
    exp = getattr(inputs, "experience", "") or ""
    days = getattr(inputs, "days_per_week", None)
    equip_list = getattr(inputs, "equipment", None) or []
    equip = ", ".join(equip_list) if isinstance(equip_list, list) else str(equip_list or "")
    parts = [goal, exp]
    if days:
        parts.append(f"{days} days/week")
    if equip:
        parts.append(f"equipment: {equip}")
    return ", ".join([p for p in parts if p]).strip(", ")

def _default_canonical_week(inputs: InputsV11) -> List[Dict[str, Any]]:
    # Build a 2× per-week exposure structure by goal; default dpw=5 for hypertrophy
    dpw = getattr(inputs, "days_per_week", None) or 5
    dpw = max(2, min(6, int(dpw)))
    goal = (inputs.goal or "hypertrophy").lower()

    def main_item(mv, s, r, notes=""):
        return {"movement": mv, "main_focus": None, "intensity_cue": "RPE 6–8", "sets": s, "reps": r, "tempo_or_rest": "60–90s", "notes": notes}
    def acc_item(mv, s, r, notes=""):
        return {"movement": mv, "sets": s, "reps": r, "tempo_or_rest": "45–75s", "notes": notes}

    days: List[Dict[str, Any]] = []
    if goal == "strength":
        template = [
            ("Mon", main_item("Back Squat", 3, 5), [acc_item("Leg Press", 3, 8), acc_item("Hamstring Curl", 3, 10)]),
            ("Tue", main_item("Bench Press", 4, 3), [acc_item("DB Row", 3, 8), acc_item("Triceps Pushdown", 3, 10)]),
            ("Thu", main_item("Deadlift", 3, 3), [acc_item("Back Extension", 3, 10), acc_item("Plank", 3, 30)]),
            ("Fri", main_item("Overhead Press", 3, 5), [acc_item("Lat Pulldown", 3, 10), acc_item("Lateral Raise", 3, 12)]),
        ]
        for name, main, acc in template[:dpw]:
            days.append({"day": name, "day_name": name, "main": [main], "accessory": acc, "prehab": [], "cardio_notes": []})
        return days

    if goal == "endurance":
        for name in ["Mon", "Wed", "Fri", "Sun"][:dpw]:
            cardio = [{"movement": "Zone 2 Cardio", "duration": "30–45 min", "tempo_or_rest": "Zone 2", "notes": ""}]
            days.append({"day": name, "day_name": name, "main": [], "accessory": [], "prehab": [], "cardio_notes": cardio})
        return days

    if goal == "fat_loss":
        template = [
            ("Mon", main_item("Back Squat", 3, 8), [acc_item("Leg Press", 3, 12), acc_item("Calf Raise", 3, 15)], [{"movement": "Zone 2 Cardio", "duration":"20–30 min","tempo_or_rest":"Zone 2","notes":""}]),
            ("Tue", main_item("Bench Press", 3, 8), [acc_item("DB Row", 3, 12), acc_item("Face Pull", 3, 15)], []),
            ("Thu", main_item("Romanian Deadlift", 3, 8), [acc_item("Hamstring Curl", 3, 12), acc_item("Reverse Lunge", 3, 10)], [{"movement": "Zone 2 Cardio", "duration":"20–30 min","tempo_or_rest":"Zone 2","notes":""}]),
            ("Fri", main_item("Overhead Press", 3, 8), [acc_item("Lat Pulldown", 3, 12), acc_item("Biceps Curl", 3, 12)], []),
        ]
        for name, main, acc, cardio in template[:dpw]:
            days.append({"day": name, "day_name": name, "main": [main], "accessory": acc, "prehab": [], "cardio_notes": cardio})
        return days

    # hypertrophy default (5‑day: Upper A / Lower A / Upper B / Lower B / Pull/Arms)
    template = [
        ("Mon", main_item("Bench Press", 3, 8), [acc_item("Incline DB Press", 3, 10), acc_item("Lateral Raise", 3, 12), acc_item("Triceps Pushdown", 3, 12)]),
        ("Tue", main_item("Back Squat", 3, 8), [acc_item("Leg Press", 3, 12), acc_item("Leg Curl", 3, 12), acc_item("Calf Raise", 3, 15)]),
        ("Wed", main_item("Barbell Row", 3, 8), [acc_item("Lat Pulldown", 3, 10), acc_item("Rear Delt Fly", 3, 12), acc_item("Biceps Curl", 3, 12)]),
        ("Thu", main_item("Romanian Deadlift", 3, 8), [acc_item("Split Squat", 3, 10), acc_item("Hamstring Curl", 3, 12), acc_item("Back Extension", 3, 12)]),
        ("Fri", main_item("Overhead Press", 3, 8), [acc_item("DB Row", 3, 10), acc_item("Face Pull", 3, 12), acc_item("Cable Fly", 3, 12)]),
    ]
    for name, main, acc in template[:dpw]:
        days.append({"day": name, "day_name": name, "main": [main], "accessory": acc, "prehab": [], "cardio_notes": []})
    return days

def _coerce_items(items: Any) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if items is None:
        return out
    if isinstance(items, dict):
        return [items]
    if isinstance(items, list):
        for it in items:
            if isinstance(it, dict):
                out.append(it)
            else:
                out.append({"movement": str(it)})
        return out
    return [{"movement": str(items)}]

def _flatten_week(week_label: str, days: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for d in days or []:
        day = _coerce_day(d.get("day", 1))
        day_name = d.get("day_name") or DAY_NAMES.get(day, f"Day {day}")
        for section in ("main", "accessory", "prehab", "cardio_notes"):
            for item in _coerce_items(d.get(section)):
                out.append({
                    "week_label": week_label,
                    "day": day,
                    "day_name": day_name,
                    "block_type": section,
                    "movement": item.get("movement", "Unknown"),
                    "main_focus": item.get("main_focus"),
                    "intensity_cue": item.get("intensity_cue"),
                    "sets": _parse_int_lower_bound(item.get("sets")),
                    "reps": _parse_int_lower_bound(item.get("reps")),
                    "duration": item.get("duration"),
                    "tempo_or_rest": item.get("tempo_or_rest"),
                    "notes": item.get("notes"),
                })
    return out

def _rotate_days(days: List[Dict[str, Any]], shift: int) -> List[Dict[str, Any]]:
    # Rotate the day sequence to change when muscles are hit across weeks
    if not days:
        return days
    shift = shift % len(days)
    return days[shift:] + days[:shift]

_ALT_ACCESSORY = {
    "Leg Press": "Hack Squat",
    "Leg Curl": "Seated Leg Curl",
    "DB Row": "Chest Supported Row",
    "Lat Pulldown": "Pull-Up",
    "Lateral Raise": "Cable Lateral Raise",
    "Triceps Pushdown": "Overhead Triceps Extension",
    "Biceps Curl": "Incline DB Curl",
    "Rear Delt Fly": "Reverse Pec Deck",
    "Face Pull": "Cable External Rotation",
    "Cable Fly": "Machine Chest Fly",
    "Split Squat": "Leg Extension",
    "Hamstring Curl": "Nordic Curl",
}

def _variant_rows(rows: List[Dict[str, Any]], week_note: str, week_idx: int) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for r in rows:
        nr = dict(r)
        nr["week_label"] = f"Week {week_idx}"
        # Accessory variation: swap to an alternative variant for weeks > 1
        if nr.get("block_type") == "accessory" and week_idx > 1:
            mv = nr.get("movement")
            if mv in _ALT_ACCESSORY:
                nr["movement"] = _ALT_ACCESSORY[mv]
        # Append simple note to guide weekly progression
        existing = (nr.get("notes") or "").strip()
        nr["notes"] = (f"{existing} | {week_note}".strip(" |")) if week_note else existing
        out.append(nr)
    return out

def assess_tweak(goal: str, tweak_text: str) -> Dict[str, Any]:
    if not tweak_text or not tweak_text.strip():
        return {"verdict": "ok", "rationale": "No tweak provided.", "citations": [], "sources": []}
    hits = retrieve_snippets({"query": f"{goal}. Consider tweak: {tweak_text}", "evidence": "evidence", "top_k": 6})
    numbered = render_numbered_snippets([h.get("text", "") for h in hits])
    user = TWEAK_ASSESSOR_USER.format(goal=goal, tweak=tweak_text, snippets=numbered)
    schema = {
        "type": "object",
        "properties": {
            "verdict": {"type": "string", "enum": ["ok", "warn", "block"]},
            "rationale": {"type": "string"},
            "citations": {"type": "array", "items": {"type": "integer"}},
        },
        "required": ["verdict", "rationale", "citations"],
        "additionalProperties": False,
    }
    out = call_llm_json_object(f"{TWEAK_ASSESSOR_SYSTEM}\n\n{user}", schema)
    out["sources"] = [{"n": i + 1, "chunk_id": h.get("id"), "doc_id": h.get("doc_id")} for i, h in enumerate(hits)]
    return out

def generate_plan_v11(inputs: InputsV11, tweak_note: Optional[str] = None) -> PlanV11:
    pal_value = PALMAP[inputs.pal_code]
    bmr = bmr_mifflin_st_jeor(inputs.sex, inputs.weight_kg, inputs.height_cm, inputs.age)
    tdee = tdee_from_bmr(bmr, pal_value)

    # Retrieval (server-side logging only)
    retrieval_query = _make_retrieval_query(inputs)
    try:
        snippet_hits = retrieve_snippets({"query": retrieval_query, "domains": getattr(inputs, "domain_filters", None), "evidence": "evidence", "top_k": 6})
    except Exception as e:
        print(f"[Plan] RAG disabled or failed: {e}")
        snippet_hits = []
    if snippet_hits:
        for i, s in enumerate(snippet_hits, 1):
            print(f"[Sources] [{i}] doc {s.get('doc_id')} · chunk {s.get('id')}")
    snippets_text = render_snippets_for_v11([s.get("text", "") for s in snippet_hits]) if snippet_hits else "- none"

    # Prompt for canonical week + progression (token-light), tolerate empty response
    user_prompt = USER_TEMPLATE_V11.format(
        sex=inputs.sex, age=inputs.age, height_cm=inputs.height_cm, weight_kg=inputs.weight_kg,
        pal_value=pal_value, goal=inputs.goal, equipment=inputs.equipment or [],
        bmr=bmr, tdee=tdee, days_per_week=getattr(inputs, "days_per_week", None) or 5,
        snippets=snippets_text, tweak=tweak_note or "",
    )
    prompt = SYSTEM_PROMPT_V11 + "\n" + user_prompt
    schema = {"type": "object"}  # advisory
    compact = call_llm_json_object(prompt, schema) or {}
    canon_days = ((compact.get("canonical_week") or {}).get("days")) or _default_canonical_week(inputs)
    week1_rows = _flatten_week("Week 1", canon_days)

    # Expand to Weeks 2–4 with day rotation and accessory variants
    dpw = getattr(inputs, "days_per_week", None) or 5
    rotated_rows_all: List[Dict[str, Any]] = []
    rotated_rows_all += week1_rows
    week_notes = {2: "+1 rep per set", 3: "+2.5–5% load", 4: "deload 15–25%"}
    # Build rotated canonical days then flatten for each week
    for wk in (2, 3, 4):
        rotated_days = _rotate_days(canon_days, shift=wk - 1)
        wk_rows_base = _flatten_week(f"Week {wk}", rotated_days)
        wk_rows = _variant_rows(wk_rows_base, week_notes.get(wk, ""), wk)
        rotated_rows_all += wk_rows

    rows_json = _sanitize_rows(rotated_rows_all := rotated_rows_all)  # type: ignore
    try:
        rows: List[PlanRowV11] = [PlanRowV11(**r) for r in rows_json]
    except ValidationError:
        repaired = _second_pass_repair(rows_json)
        rows = [PlanRowV11(**r) for r in repaired]

    priority = {"main": 0, "accessory": 1, "prehab": 2, "cardio_notes": 3}
    rows.sort(key=lambda r: (r.week_label, r.day, priority.get(r.block_type, 9)))

    plan = PlanV11(goal=inputs.goal, rows=rows, week_count=4)
    plan.extra = {"snippets_count": len(snippet_hits), "retrieval_query": retrieval_query}
    return plan

# Helpers reused from earlier implementation
def _sanitize_rows(rows_json: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    cleaned: List[Dict[str, Any]] = []
    per_day_seen: Dict[int, int] = {}
    for r in rows_json:
        day = _coerce_day(r.get("day", 1))
        per_day_seen[day] = per_day_seen.get(day, 0) + 1
        week_label = r.get("week_label") or "Week 1"
        day_name = r.get("day_name") or DAY_NAMES.get(day, f"Day {day}")
        block_type = r.get("block_type") or ("main" if per_day_seen[day] == 1 else "accessory")
        movement = r.get("movement") or "Unknown"
        cleaned.append({
            "week_label": week_label, "day": day, "day_name": day_name, "block_type": block_type,
            "movement": movement, "main_focus": r.get("main_focus"), "intensity_cue": r.get("intensity_cue"),
            "sets": _parse_int_lower_bound(r.get("sets")), "reps": _parse_int_lower_bound(r.get("reps")),
            "duration": r.get("duration"), "tempo_or_rest": r.get("tempo_or_rest"), "notes": r.get("notes"),
        })
    return cleaned

def _second_pass_repair(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    repaired: List[Dict[str, Any]] = []
    for r in rows:
        if not isinstance(r.get("day"), int) or r.get("movement") in (None, "", "Unknown"):
            r["movement"] = r.get("movement") or "Unknown"
        r["sets"] = r["sets"] if isinstance(r.get("sets"), int) else None
        r["reps"] = r["reps"] if isinstance(r.get("reps"), int) else None
        repaired.append(r)
    return repaired
