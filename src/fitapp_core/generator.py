# Pure Python module implementing the rules‑first workout plan generator so logic is reusable, testable, and decoupled from UI per Python structuring guidelines.

from typing import Dict, Any

SAMPLE_DAY = [
    {"name": "Squat", "sets": 3, "reps": "8–10", "rest_s": 90},
    {"name": "Push-up", "sets": 3, "reps": "AMRAP", "rest_s": 60},
    {"name": "Row", "sets": 3, "reps": "10–12", "rest_s": 90},
]

def generate_plan(profile: Dict[str, Any]) -> Dict[str, Any]:
    days = int(profile.get("days_per_week", 4))
    plan = {"profile": profile, "days": []}
    for i in range(1, days + 1):
        plan["days"].append({"day": i, "exercises": SAMPLE_DAY})
    return plan
