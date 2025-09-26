# =========================
# Page: Plan (v1.1 engine)
# =========================
# Renders the plan using the new goal-agnostic v1.1 layout.
# v1 remains in the codebase for rollback (separate page or flag).

import streamlit as st
import pandas as pd
from fitapp_core.plan_v11 import generate_plan_v11
from fitapp_core.models_v11 import InputsV11

# ---------- Page title ----------
st.title("Plan")

# ---------- Guard: prerequisites ----------
if "inputs_v1" not in st.session_state:
    st.info("No inputs yet. Go to Onboarding to enter details.")
    st.stop()

# ---------- Cache: v1.1 plan generation ----------
@st.cache_data(show_spinner=True)
def cached_generate_plan_v11(inputs_dict: dict, tweak_note: str | None):
    """Cache the v1.1 generation on a plain dict for deterministic reruns."""
    inputs = InputsV11(**inputs_dict)
    plan = generate_plan_v11(inputs, tweak_note=tweak_note)
    return plan.model_dump()

# ---------- Inputs conversion: v1 -> v1.1 ----------
v1 = st.session_state["inputs_v1"].model_dump()
inputs_v11 = {
    "age": v1["age"],
    "sex": v1["sex"],
    "height_cm": v1["height_cm"],
    "weight_kg": v1["weight_kg"],
    "pal_code": v1["pal_code"],
    "goal": v1["goal"],
    "equipment": v1.get("equipment"),
    "notes": v1.get("notes"),
}

# ---------- Tweak box (unique key to avoid duplicate IDs) ----------
existing_plan_id = st.session_state.get("plan_v11", {}).get("plan_id", "current")
tweak = st.text_input(
    "Suggest a tweak (optional)",
    placeholder="e.g., swap squats for leg press",
    key=f"tweak_v11_{existing_plan_id}",
)

# ---------- Generate plan & persist ----------
plan_dict = cached_generate_plan_v11(inputs_v11, tweak)
st.session_state["plan_v11"] = plan_dict
plan_id = plan_dict["plan_id"]

# ---------- Grouped day/sections view with inline edits ----------
df = pd.DataFrame(plan_dict["rows"])

for (week, day, day_name), g in df.groupby(["week_label", "day", "day_name"], sort=True):
    st.subheader(f"{week} - {day_name}")  # ASCII dash avoids PDF font issues later

    # Render sections in a consistent order
    for block in ["main", "accessory", "prehab", "cardio_notes"]:
        sub = g[g["block_type"] == block]
        if sub.empty:
            continue

        st.caption(block.replace("_", " ").title())

        editable_cols = ["sets", "reps", "duration", "tempo_or_rest", "notes"]
        disabled_cols = [c for c in sub.columns if c not in editable_cols]

        editor_key = f"editor_{plan_id}_{week}_{day}_{block}"
        edited = st.data_editor(
            sub[disabled_cols + editable_cols],
            hide_index=True,
            width="stretch",          # replaces deprecated use_container_width
            disabled=disabled_cols,
            key=editor_key,           # unique per day+section
        )

        # Persist edits back into the aggregated dataframe
        df.loc[edited.index, editable_cols] = edited[editable_cols]

# ---------- Save edited rows to session for Export page ----------
plan_dict["rows"] = df.to_dict(orient="records")
st.session_state["plan_v11"] = plan_dict

# ---------- Summary line ----------
st.caption(f"Goal: {plan_dict['goal']} - Weeks: {plan_dict.get('week_count', 4)}")
