from fitapp_core.exporters.json_csv import to_json_bytes, to_csv_str
from fitapp_core.exporters.pdf import build_pdf

def sample_plan():
    return {
        "schema_version": "1",
        "plan_id": "abc123",
        "generated_at": "2025-09-17T00:00:00Z",
        "goal": "hypertrophy",
        "pal_value": 1.85,
        "bmr": 1700,
        "tdee": 3145,
        "rows": [
            {"day": 1, "movement": "Squat", "sets": 3, "reps": 8,
             "tempo_or_rest": "2-0-2", "load_prescription": "RPE 7", "notes": ""},
        ],
    }

def test_json_export_includes_schema_and_id():
    data = to_json_bytes(sample_plan())
    s = data.decode("utf-8")
    assert '"schema_version": "1"' in s and '"plan_id": "abc123"' in s

def test_csv_export_header_and_row():
    rows = sample_plan()["rows"]
    csv_str = to_csv_str(rows)
    lines = [ln for ln in csv_str.splitlines() if ln]
    assert lines[0] == "day,movement,sets,reps,tempo_or_rest,load_prescription,notes"
    assert "Squat" in lines[1]

def test_pdf_export_bytes_nonempty():
    pdf_bytes = build_pdf(sample_plan())
    assert isinstance(pdf_bytes, (bytes, bytearray)) and len(pdf_bytes) > 100
    assert pdf_bytes.startswith(b"%PDF")
