import pytest
from fitapp_core.models import Inputs
from fitapp_core.plan_v1 import generate_plan_v1

@pytest.mark.xfail(reason="deprecated, kept for rollback safety")
def test_generate_plan_v1_basic():
    inp = Inputs(age=25, sex="male", height_cm=175, weight_kg=70.0,
                 pal_code="active", goal="hypertrophy")
    plan = generate_plan_v1(inp)
    assert plan.schema_version == "1"
    assert isinstance(plan.bmr, int) and plan.bmr > 0
    assert isinstance(plan.tdee, int) and plan.tdee > 0
    assert plan.goal == "hypertrophy"
    assert len(plan.rows) >= 1
    for r in plan.rows:
        assert r.day >= 1 and r.sets >= 1 and r.reps >= 1
