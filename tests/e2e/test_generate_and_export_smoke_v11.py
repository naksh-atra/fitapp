# tests/e2e/test_generate_and_export_smoke_v11.py
import pytest
from fitapp_core.models_v11 import InputsV11
from fitapp_core.plan_v11 import generate_plan_v11
from fitapp_core.exporters.json_csv import to_csv_str_v11, to_json_bytes
from fitapp_core.exporters.pdf import build_pdf_v11

def test_e2e_generate_and_export(monkeypatch, inputs_v11_dict, raw_rows_dirty_v11, tmp_path):
    from fitapp_core import plan_v11 as mod
    monkeypatch.setattr(mod, "call_llm_json", lambda prompt: raw_rows_dirty_v11)

    inputs = InputsV11(**inputs_v11_dict)
    plan = generate_plan_v11(inputs)

    assert plan.schema_version == "1.1"
    assert plan.goal == inputs.goal
    assert len(plan.rows) >= 1

    csv_text = to_csv_str_v11([r.model_dump() for r in plan.rows])
    (tmp_path / "plan.csv").write_text(csv_text, encoding="utf-8")

    jb = to_json_bytes(plan.model_dump())
    (tmp_path / "plan.json").write_bytes(jb)

    pdf_bytes = build_pdf_v11(plan.model_dump())
    (tmp_path / "plan.pdf").write_bytes(pdf_bytes)
