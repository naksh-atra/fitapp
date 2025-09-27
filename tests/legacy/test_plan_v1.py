import pytest
import importlib

@pytest.mark.xfail(reason="legacy v1 path deprecated; kept for rollback safety")
def test_generate_plan_v1_basic(monkeypatch):
    # Ensure env var exists before imports that init clients
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    # Stub LLM to avoid network
    llm = importlib.import_module("fitapp_core.rag.llm")
    monkeypatch.setattr(llm, "call_llm_json", lambda prompt: [
        {"day": 1, "movement": "Bench Press", "sets": 3, "reps": 8}
    ])  
    models = importlib.import_module("fitapp_core.models")
    plan_v1 = importlib.import_module("fitapp_core.plan_v1")

    inp = models.Inputs(age=25, sex="male", height_cm=175, weight_kg=70.0,
                        pal_code="active", goal="hypertrophy")
    plan = plan_v1.generate_plan_v1(inp)
    assert plan.goal == "hypertrophy"