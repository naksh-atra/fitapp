import pytest
from fitapp_core.models_v11 import InputsV11, PlanRowV11

def test_inputs_valid():
    inp = InputsV11(
        age=25,
        sex="male",
        height_cm=175,
        weight_kg=70.0,
        pal_code="active",
        goal="hypertrophy",
        equipment=["barbell", "dumbbell"],
        notes=None,
    )
    assert inp.goal == "hypertrophy"
    assert inp.height_cm > 0 and inp.weight_kg > 0

def test_planrow_v11_defaults_and_types():
    # Missing optional fields should default/allow None; required fields must exist
    row = PlanRowV11(
        week_label="Week 1",
        day=1,
        day_name="Mon",
        block_type="main",
        movement="Bench Press",
        sets=3,
        reps=8,
    )
    assert row.week_label == "Week 1"
    assert row.block_type in {"main","accessory","prehab","cardio_notes"}
    # Optional fields present but may be None
    assert hasattr(row, "duration")
    assert hasattr(row, "tempo_or_rest")
