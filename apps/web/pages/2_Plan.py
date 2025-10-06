# # apps/web/pages/2_Plan.py
# from __future__ import annotations

# import streamlit as st
# import pandas as pd
# from collections import defaultdict

# from fitapp_core.plan_v11 import generate_plan_v11, assess_tweak
# from fitapp_core.models_v11 import InputsV11
# from fitapp_core.rag.retriever import retrieve_snippets

# DAY_ORDER = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# st.title("Plan")

# # Prereq
# if "inputs_v1" not in st.session_state:
#     st.info("No inputs yet. Go to Onboarding to enter details.")
#     st.stop()

# @st.cache_data(show_spinner=True)
# def cached_generate_plan_v11(inputs_dict: dict, tweak_note: str | None):
#     inputs = InputsV11(**inputs_dict)
#     plan = generate_plan_v11(inputs, tweak_note=tweak_note)
#     return plan.model_dump()

# # v1 -> v1.1 dict
# v1 = st.session_state["inputs_v1"].model_dump()
# inputs_v11 = {
#     "age": v1["age"],
#     "sex": v1["sex"],
#     "height_cm": v1["height_cm"],
#     "weight_kg": v1["weight_kg"],
#     "pal_code": v1["pal_code"],
#     "goal": v1["goal"],
#     "equipment": v1.get("equipment"),
#     "notes": v1.get("notes"),
#     "experience": v1.get("experience"),
#     "days_per_week": v1.get("days_per_week"),
# }

# # Tweak field (stable key across regenerations)
# existing_plan_id = st.session_state.get("plan_v11", {}).get("plan_id", "current")
# tweak = st.text_input(
#     "Suggest a tweak (optional)",
#     placeholder="e.g., swap squats for leg press",
#     key=f"tweak_v11_{existing_plan_id}",
# )

# # Generate initial plan
# plan_dict = cached_generate_plan_v11(inputs_v11, None)
# st.session_state["plan_v11"] = plan_dict
# plan_id = plan_dict.get("plan_id", "current")
# st.caption(f"RAG: {plan_dict.get('extra',{}).get('snippets_count', 0)} snippets")

# # Unified tweak flow
# def run_assess_and_apply():
#     verdict = assess_tweak(inputs_v11.get("goal", ""), tweak or "")
#     st.session_state["tweak_verdict"] = verdict
#     if verdict["verdict"] == "block":
#         st.error(verdict["rationale"])
#         return None
#     if verdict["verdict"] == "warn":
#         st.warning(verdict["rationale"])
#         if not st.session_state.get("confirm_apply_warn"):
#             st.session_state["confirm_apply_warn"] = True
#             return None
#     # ok or confirmed warn -> regenerate with tweak
#     applied = cached_generate_plan_v11(inputs_v11, tweak)
#     st.session_state["plan_v11"] = applied
#     return applied

# if st.button("Assess & apply tweak"):
#     st.session_state["confirm_apply_warn"] = False
#     res = run_assess_and_apply()
#     if res is not None:
#         plan_dict = res

# # If a warn was shown, offer confirm button
# if st.session_state.get("confirm_apply_warn"):
#     if st.button("Confirm and apply"):
#         res = run_assess_and_apply()
#         if res is not None:
#             plan_dict = res
#     v = st.session_state.get("tweak_verdict")
#     if v:
#         for s in v.get("sources", []):
#             st.caption(f"[{s['n']}] doc {s.get('doc_id','?')} · chunk {s.get('chunk_id','?')}")

# # View toggle
# view = st.radio("View", ["Blueprint (Week 1)", "Month (4 weeks)"], horizontal=True)

# # Helpers to render compact cell strings
# def _cell_lines(day_rows: pd.DataFrame) -> list[str]:
#     lines: list[str] = []
#     # Keep order: main -> accessory -> prehab -> cardio_notes
#     for section in ["main", "accessory", "prehab", "cardio_notes"]:
#         sub = day_rows[day_rows["block_type"] == section]
#         for _, r in sub.iterrows():
#             vol = f"{int(r['sets'])}×{int(r['reps'])}" if pd.notna(r.get("sets")) and pd.notna(r.get("reps")) else (r.get("duration") or "")
#             base = f"{r['movement']} — {vol}".strip(" —")
#             note = (r.get("notes") or "").strip()
#             lines.append(f"{base}" if not note else f"{base} · {note}")
#     return lines or ["(no items)"]

# rows = plan_dict.get("rows") or []
# if not rows:
#     st.error("Plan is empty; try again or adjust your tweak.")
#     st.stop()

# df = pd.DataFrame(rows)

# # Derive week/day availability from rows
# weeks = sorted(df["week_label"].dropna().unique().tolist(), key=lambda x: (int(x.split()[-1]) if str(x).startswith("Week") else 1))
# day_order = [d for d in DAY_ORDER if d in set(df["day_name"].dropna())]
# if not day_order:
#     day_order = DAY_ORDER[: (inputs_v11.get("days_per_week") or 4)]

# if view.startswith("Blueprint"):
#     # Filter to Week 1
#     d1 = df[df["week_label"] == "Week 1"]
#     for dn in day_order:
#         g = d1[d1["day_name"] == dn]
#         if g.empty:
#             continue
#         st.subheader(f"Week 1 - {dn}")
#         # Compact display as a bulleted list
#         for line in _cell_lines(g):
#             st.write(f"- {line}")
# else:
#     # Month grid: 4 columns (Week 1..4)
#     cols = st.columns(len(weeks) or 4)
#     by_week_day: dict[str, dict[str, list[str]]] = defaultdict(dict)
#     for wk in weeks:
#         wd = {}
#         for dn in day_order:
#             g = df[(df["week_label"] == wk) & (df["day_name"] == dn)]
#             wd[dn] = _cell_lines(g)
#         by_week_day[wk] = wd
#     for i, wk in enumerate(weeks):
#         with cols[i]:
#             st.markdown(f"#### {wk}")
#             for dn in day_order:
#                 st.caption(dn)
#                 for line in by_week_day[wk][dn]:
#                     st.write(f"- {line}")

# # Provenance / Sources
# st.subheader("Sources")
# def _make_retrieval_query(inputs_dict: dict) -> str:
#     goal = inputs_dict.get("goal") or ""
#     exp = inputs_dict.get("experience") or ""
#     days = inputs_dict.get("days_per_week") or ""
#     eq = inputs_dict.get("equipment") or []
#     equip = ", ".join(eq) if isinstance(eq, list) else str(eq)
#     parts = [goal, exp, f"{days} days/week" if days else None, f"equipment: {equip}" if equip else None]
#     return ", ".join([p for p in parts if p])

# retrieval_query = _make_retrieval_query(inputs_v11)
# sources_hits = retrieve_snippets({
#     "query": retrieval_query,
#     "domains": inputs_v11.get("domain_filters"),
#     "evidence": "evidence",
#     "top_k": 6,
# })
# if sources_hits:
#     st.session_state["plan_v11_sources"] = [
#         {"n": i + 1, "doc_id": h.get("doc_id"), "chunk_id": h.get("id")}
#         for i, h in enumerate(sources_hits)
#     ]
#     for s in st.session_state["plan_v11_sources"]:
#         st.caption(f"[{s['n']}] doc {s.get('doc_id','?')} · chunk {s.get('chunk_id','?')}")
#     st.caption(f"RAG: {len(sources_hits)} snippets")
# else:
#     st.caption("No research snippets found for this query; plan generated using defaults.")




# apps/web/pages/2_Plan.py
from __future__ import annotations

import streamlit as st
import pandas as pd
from collections import defaultdict

from fitapp_core.plan_v11 import generate_plan_v11
from fitapp_core.models_v11 import InputsV11

DAY_ORDER = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

st.title("Plan")

# ---------- Guard: prerequisites ----------
if "inputs_v1" not in st.session_state:
    st.info("No inputs yet. Go to Onboarding to enter details.")
    st.stop()

# ---------- Cache: v1.1 plan generation ----------
@st.cache_data(show_spinner=True)
def cached_generate_plan_v11(inputs_dict: dict, tweak_note: str | None):
    """
    Cache the v1.1 generation on a plain dict for deterministic reruns.
    """
    inputs = InputsV11(**inputs_dict)
    plan = generate_plan_v11(inputs, tweak_note=tweak_note)
    return plan.model_dump()

# ---------- Inputs conversion: v1 -> v1.1 ----------
v1 = st.session_state["inputs_v1"].model_dump()
# default to 5 days/week if user did not specify in onboarding
days_per_week = v1.get("days_per_week") or 5
inputs_v11 = {
    "age": v1["age"],
    "sex": v1["sex"],
    "height_cm": v1["height_cm"],
    "weight_kg": v1["weight_kg"],
    "pal_code": v1["pal_code"],
    "goal": v1["goal"],
    "equipment": v1.get("equipment"),
    "notes": v1.get("notes"),
    "experience": v1.get("experience"),
    "days_per_week": int(days_per_week),
}

# ---------- Generate plan (no tweak UI for now) ----------
plan_dict = cached_generate_plan_v11(inputs_v11, None)
if not plan_dict or not plan_dict.get("rows"):
    st.error("Plan is empty; please try regenerating or adjust inputs.")
    st.stop()

# Persist for Export page
st.session_state["plan_v11"] = plan_dict

st.caption(f"Goal: {plan_dict.get('goal','?')} — Weeks: {plan_dict.get('week_count', 4)}")

# ---------- Helpers for rendering ----------
def _cell_lines(day_rows: pd.DataFrame) -> list[str]:
    """
    Return compact lines like 'Bench Press — 3×8' with optional trailing notes.
    """
    lines: list[str] = []
    # Keep logical order
    for section in ["main", "accessory", "prehab", "cardio_notes"]:
        sub = day_rows[day_rows["block_type"] == section]
        for _, r in sub.iterrows():
            sets = r.get("sets")
            reps = r.get("reps")
            duration = r.get("duration")
            vol = f"{int(sets)}×{int(reps)}" if pd.notna(sets) and pd.notna(reps) else (duration or "")
            base = f"{r.get('movement','')} — {vol}".strip(" —")
            note = (r.get("notes") or "").strip()
            lines.append(base if not note else f"{base} · {note}")
    return lines or ["(no items)"]

def _week_sort_key(wk: str) -> int:
    try:
        return int(str(wk).split()[-1])
    except Exception:
        return 1

# ---------- Build DataFrame ----------
rows = plan_dict.get("rows") or []
df = pd.DataFrame(rows)

# Determine day order from inputs (e.g., Mon–Fri if 5)
visible_days = DAY_ORDER[: int(days_per_week)] if 2 <= int(days_per_week) <= 6 else DAY_ORDER

# ---------- View toggle ----------
view = st.radio("View", ["Blueprint (Week 1)", "Month (4 weeks)"], horizontal=True)

if view.startswith("Blueprint"):
    d1 = df[df["week_label"] == "Week 1"]
    for dn in visible_days:
        g = d1[d1["day_name"] == dn]
        if g.empty:
            continue
        st.subheader(f"Week 1 — {dn}")
        for line in _cell_lines(g):
            st.write(f"- {line}")
else:
    # Month grid: show Week 1..4 in columns; each cell is a compact bulleted list
    weeks = sorted(df["week_label"].dropna().unique().tolist(), key=_week_sort_key)
    if not weeks:
        weeks = ["Week 1", "Week 2", "Week 3", "Week 4"]
    cols = st.columns(len(weeks))
    for i, wk in enumerate(weeks):
        with cols[i]:
            st.markdown(f"#### {wk}")
            for dn in visible_days:
                g = df[(df["week_label"] == wk) & (df["day_name"] == dn)]
                if g.empty:
                    continue
                st.caption(dn)
                for line in _cell_lines(g):
                    st.write(f"- {line}")

# ---------- Notes ----------
# Sources are intentionally not displayed on this page; they are logged server-side during plan generation.
# See console logs from fitapp_core.plan_v11.generate_plan_v11 for doc/chunk provenance.
