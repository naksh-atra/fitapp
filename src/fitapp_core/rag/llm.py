from typing import List, Dict

def call_llm_json(prompt: str) -> List[Dict]:
    return [
        {"day": 1, "movement": "Squat", "sets": 3, "reps": 8, "tempo_or_rest": "2-0-2", "load_prescription": "RPE 7", "notes": "Warm-up first."},
        {"day": 1, "movement": "Bench Press", "sets": 3, "reps": 8, "tempo_or_rest": "2-1-2", "load_prescription": "RPE 7", "notes": ""},
        {"day": 2, "movement": "Deadlift", "sets": 3, "reps": 5, "tempo_or_rest": "1-0-1", "load_prescription": "RPE 8", "notes": "Straps optional."},
    ]
