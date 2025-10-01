# v1 (keep for reference if needed)
SYSTEM_PROMPT = """You are a cautious workout-planning assistant.
Return ONLY JSON array with fields: day, movement, sets, reps, tempo_or_rest, load_prescription, notes.
If evidence is insufficient, return an empty array."""

USER_TEMPLATE = """Inputs:
- age={age}, sex={sex}, height_cm={height_cm}, weight_kg={weight_kg}
- PAL={pal_value} (TDEE={tdee} kcal/day), goal={goal}
Evidence:
{snippets}
Constraints:
- Safe, common exercises; equipment-agnostic when uncertain.
- Output strict JSON array only.
"""

# v1.1 (in use)
SYSTEM_PROMPT_V11 = """You format workout plans as clear weekly schedules.
Return ONLY a JSON array of objects with fields:
week_label, day, day_name, block_type, movement, main_focus, intensity_cue,
sets, reps, duration, tempo_or_rest, notes.
- Use block_type one of: main, accessory, prehab, cardio_notes.
- If a field is not applicable (e.g., duration for main), omit it or set it to null.
- Do not include any text outside the JSON array.
"""

# RAG-ready user template extension:
# - Adds an optional Evidence section to ground choices.
# - Keeps JSON-only requirement intact.
USER_TEMPLATE_V11 = """Inputs:
- sex={sex}, age={age}, height_cm={height_cm}, weight_kg={weight_kg}, PAL={pal_value}
- goal={goal}, equipment={equipment}
Energy:
- BMR={bmr} kcal/day, TDEE≈{tdee} kcal/day
Style guide:
- Weekly view with day headers; sections: Main, Accessories, Prehab, Cardio/Notes.
- Main includes main_focus and intensity_cue (e.g., %1RM, RPE, or Zone).
- Accessories: 6–15 reps typical; Prehab concise; Cardio lists duration/zone.
- Provide 4 weeks by default; deload as appropriate for the goal.

Evidence (optional excerpts to guide choices):
{snippets}

Rules:
- Ground exercise selection, rep ranges, and intensity cues in Evidence when provided.
- Do not quote or copy Evidence; use it to choose appropriate values.
- If Evidence is insufficient, choose reasonable defaults consistent with the style guide.
- Output must be ONLY a JSON array; no extra commentary.

User tweak:
{tweak}
"""

# Helper to format top-k retrieved snippets for the template
def render_snippets_for_v11(snippets_texts):
    # Concise bullets; keep under token limits
    out = []
    for i, t in enumerate(snippets_texts, 1):
        t = t.strip().replace("\n", " ")
        if len(t) > 400:
            t = t[:397] + "..."
        out.append(f"- [{i}] {t}")
    return "\n".join(out)
