import pytest

from fitapp_core.models_v11 import InputsV11, PlanRowV11
from fitapp_core.plan_v11 import generate_plan_v11

# ---- Fixtures ----

@pytest.fixture
def inputs_v11():
    return InputsV11(
        age=25,
        sex="male",
        height_cm=175,
        weight_kg=70.0,
        pal_code="active",
        goal="hypertrophy",
        equipment=["barbell", "dumbbell"],
    )

@pytest.fixture
def raw_rows_dirty():
    # Intentionally missing required v1.1 fields + string ranges to trigger sanitizer
    return [
        {"day": 1, "movement": "Barbell Bench Press", "sets": "3-6", "reps": 8},
        {"day": 1, "movement": "Triceps Pushdown", "sets": "3", "reps": "10-12"},
        {"day": 1, "movement": "Dumbbell Bench Press", "sets": 3, "reps": 8},
    ]

@pytest.fixture
def raw_rows_clean():
    # Fully specified v1.1 rows to confirm normal path
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


# ---- Tests ----

def test_generate_plan_v11_from_dirty_llm_output(monkeypatch, inputs_v11, raw_rows_dirty):
    """
    The LLM returns partial/dirty rows; sanitizer must fill week_label/day_name/block_type
    and coerce ranges to ints so Pydantic validation succeeds.
    """
    from fitapp_core import plan_v11 as mod
    monkeypatch.setattr(mod, "call_llm_json", lambda prompt: raw_rows_dirty)
    plan = generate_plan_v11(inputs_v11)
    assert plan.schema_version == "1.1"
    assert plan.goal == "hypertrophy"
    assert len(plan.rows) >= 1
    # Validate required fields and reasonable typing
    first = plan.rows[0]
    assert first.week_label.startswith("Week ")
    assert first.day_name in {"Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"}
    assert first.block_type in {"main", "accessory", "prehab", "cardio_notes"}
    # sets/reps may be None for cardio sections; otherwise ints
    if first.block_type in {"main", "accessory"}:
        assert (first.sets is None) or isinstance(first.sets, int)
        assert (first.reps is None) or isinstance(first.reps, int)
    # Ensure every row validates under the model
    for r in plan.rows:
        # round-trip through model to assert schema compliance
        PlanRowV11(**r.model_dump())

@pytest.mark.parametrize("which", ["dirty", "clean"])
def test_generate_plan_v11_parametrized(monkeypatch, inputs_v11, raw_rows_dirty, raw_rows_clean, which):
    """
    Parametrized check to cover both sanitize path (dirty) and normal path (clean),
    ensuring stable ordering by (week, day, block_type).
    """
    from fitapp_core import plan_v11 as mod
    raw = raw_rows_dirty if which == "dirty" else raw_rows_clean
    monkeypatch.setattr(mod, "call_llm_json", lambda prompt: raw)

    plan = generate_plan_v11(inputs_v11)
    assert plan.schema_version == "1.1"
    # Order: main appears before accessory for the same day
    same_day = [r for r in plan.rows if r.day == plan.rows[0].day]
    block_order = [r.block_type for r in same_day]
    if "main" in block_order and "accessory" in block_order:
        assert block_order.index("main") <= block_order.index("accessory")