# tests/conftest.py
import pytest
import os

# # --- Early env guard for modules that init clients at import time ---
# @pytest.fixture(scope="session", autouse=True)
# def _set_dummy_api_key_for_imports():
#     # Ensure present during collection/import of modules like rag.llm
#     os.environ.setdefault("OPENAI_API_KEY", "test")

# Ensure present during collection/import of modules that init clients at import time
os.environ.setdefault("OPENAI_API_KEY", "test")

# ----- Shared v1.1 fixtures -----

@pytest.fixture
def inputs_v11_dict():
    return {
        "age": 28,
        "sex": "male",
        "height_cm": 178,
        "weight_kg": 76,
        "pal_code": "active",
        "goal": "hypertrophy",
        "equipment": ["barbell", "dumbbell", "cable"],
        "notes": None,
    }

@pytest.fixture
def raw_rows_clean_v11():
    return [
        {
            "week_label": "Week 1",
            "day": 1,
            "day_name": "Mon",
            "block_type": "main",
            "movement": "Barbell Bench Press",
            "main_focus": "Bench Volume",
            "intensity_cue": "RPE 7",
            "sets": 3,
            "reps": 8,
        },
        {
            "week_label": "Week 1",
            "day": 1,
            "day_name": "Mon",
            "block_type": "accessory",
            "movement": "Triceps Pushdown",
            "sets": 3,
            "reps": 10,
        },
    ]

@pytest.fixture
def raw_rows_dirty_v11():
    # Missing fields + ranges to exercise sanitizer
    return [
        {"day": 1, "movement": "Barbell Bench Press", "sets": "3-6", "reps": 8},
        {"day": 1, "movement": "Triceps Pushdown", "sets": "3", "reps": "10-12"},
    ]


# ----- Optional: global LLM stub switch -----
# If ever needed, uncomment to force stub across the suite
# @pytest.fixture(autouse=True)
# def _stub_llm_everywhere(monkeypatch):
#     try:
#         from fitapp_core import plan_v11 as mod
#         monkeypatch.setattr(mod, "call_llm_json", lambda prompt: [
#             {"day": 1, "movement": "Bench", "sets": "3-6", "reps": 8}
#         ])
#     except Exception:
#         # Some test modules don't import plan_v11; ignore
#         pass
