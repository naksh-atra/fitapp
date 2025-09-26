# #v1
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



# v1.1
SYSTEM_PROMPT_V11 = """You format workout plans as clear weekly schedules.
Return ONLY a JSON array of objects with fields:
week_label, day, day_name, block_type, movement, main_focus, intensity_cue,
sets, reps, duration, tempo_or_rest, notes.
- Use block_type one of: main, accessory, prehab, cardio_notes.
- If a field is not applicable (e.g., duration for main), omit it or set it to null.
- Do not include any text outside the JSON array.
"""

USER_TEMPLATE_V11 = """Inputs:
- sex={sex}, age={age}, height_cm={height_cm}, weight_kg={weight_kg}, PAL={pal_value}
- goal={goal}, equipment={equipment}
Energy:
- BMR={bmr} kcal/day, TDEE≈{tdee} kcal/day
Style guide:
- Weekly view with day headers; sections: Main, Accessories, Prehab, Cardio/Notes.
- Main includes main_focus and intensity_cue (e.g., %1RM, RPE, or Zone).
- Accessories: 6–15 reps typical; Prehab concise; Cardio lists duration/zone.
- Keep notes short and safety‑aware.
- Provide 4 weeks by default; deload as appropriate for the goal.
Evidence (optional):
{snippets}
User tweak:
{tweak}
"""
